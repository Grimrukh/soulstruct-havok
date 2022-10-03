"""Manager class that combines various HKX files to make animation modification easier.

Currently mainly set up for Havok 2015 (for Nightfall/DSR).
"""
from __future__ import annotations

import abc
import copy
import logging
import typing as tp
from pathlib import Path

from soulstruct.base.game_file import GameFile
from soulstruct.containers import Binder
from soulstruct.utilities.maths import *

from soulstruct_havok.tagfile.unpacker import MissingCompendiumError
from soulstruct_havok.wrappers.base import BaseAnimationHKX, BaseSkeletonHKX
from soulstruct_havok.wrappers.base.skeleton import BONE_SPEC_TYPING
from soulstruct_havok.spline_compression import *

_LOGGER = logging.getLogger(__name__)


class BaseAnimationManager(abc.ABC):

    ANIMATION_HKX: tp.Type[BaseAnimationHKX]
    SKELETON_HKX: tp.Type[BaseSkeletonHKX]
    skeleton: BaseSkeletonHKX
    animations: dict[int, BaseAnimationHKX]
    default_anim_id: int | None

    def __init__(self, skeleton: BaseSkeletonHKX, animations: dict[int, BaseAnimationHKX]):
        self.skeleton = skeleton
        self.animations = animations
        if len(animations) == 1:
            self.default_anim_id = list(animations)[0]
        else:
            self.default_anim_id = None  # undecided

    def get_animation(self, anim_id: int = None) -> BaseAnimationHKX:
        if anim_id is None:
            if self.default_anim_id is not None:
                return self.animations[self.default_anim_id]
            raise ValueError("Default animation ID has not been set.")
        return self.animations[anim_id]

    def copy_animation(self, anim_id: int, new_anim_id: int, overwrite=False):
        """Make a deep copy of an animation instance.+"""
        if new_anim_id in self.animations and not overwrite:
            raise ValueError(f"Animation ID {new_anim_id} already exists, and `overwrite=False`.")
        self.animations[new_anim_id] = self.animations[anim_id].copy()

    def mirror_transform_bone_tracks(
        self,
        l_bone: BONE_SPEC_TYPING,
        r_bone: BONE_SPEC_TYPING,
        transform: QuatTransform,
        anim_id: int = None,
        compensate_child_bones=False,
        use_root_space=False,  # TODO: implement
    ):
        """Apply `transform` to `l_bone`, and apply another transform to `r_bone` that is the reflection of `transform`
        around the root YZ plane.

        If `use_root_space=False`, it will be assumed that the bone hierarchy is also mirrored, in which case
        reflecting `transform` in local space should still have the desired effect.
        """
        l_bone = self.skeleton.resolve_bone_spec(l_bone)
        r_bone = self.skeleton.resolve_bone_spec(r_bone)
        animation = self.get_animation(anim_id)

    def transform_bone_track(
        self,
        bone: BONE_SPEC_TYPING,
        transform: QuatTransform,
        anim_id: int = None,
        compensate_child_bones=False,
        use_root_space=False,  # TODO: implement
    ):
        """Apply `transform` to every control point or static transform in the given bone's track.

        If `compensate_child_bones=True`, the all tracks of the bone's immediate children will be counter-transformed in
        such a way that they do not move relative to this parent bone, which is useful for IK. The animation must be
        interleaved to do this, as synchonized parent-child data is needed for each frame (and I can't unpack, edit,
        and regenerate splines myself).
        """
        bone = self.skeleton.resolve_bone_spec(bone)
        animation = self.get_animation(anim_id)
        if animation.is_spline:
            track = self.get_bone_spline_animation_track(bone, anim_id)
            track.apply_transform_to_translate(transform)
            if compensate_child_bones:
                raise ValueError("Cannot use `fix_children=True` for a spline-compressed animation.")
        elif animation.is_interleaved:
            parent_transforms = self.get_bone_interleaved_transforms(bone, anim_id)
            for parent_t in parent_transforms:
                parent_t.translate = transform.apply_to_vector(parent_t.translate)
                parent_t.rotation = transform.rotation * parent_t.rotation
            if compensate_child_bones:
                child_tracks = self.get_immediate_child_bone_interleaved_animation_transforms(bone)
                for child_index, child_transforms in child_tracks:
                    for i in range(len(child_transforms)):
                        parent_t = parent_transforms[i]  # in same frame
                        child_t = child_transforms[i]
                        # Enter parent's frame.
                        child_t.translate = parent_t.apply_to_vector(child_t.translate)
                        child_t.rotation = parent_t.rotation * child_t.rotation
                        # Apply inverse transform.
                        child_t.translate = transform.apply_inverse_to_vector(child_t.translate)
                        child_t.rotation = transform.rotation.inverse() * child_t.rotation
                        # Exit parent's frame.
                        child_t.translate = parent_t.apply_inverse_to_vector(child_t.translate)
                        child_t.rotation = parent_t.rotation.inverse() * child_t.rotation

    def rotate_bone_track(self, bone: BONE_SPEC_TYPING, rotation: Quaternion, anim_id: int = None):
        """Apply `rotation` to every control point (or just the static value) of given bone track."""
        animation = self.get_animation(anim_id)
        if animation.is_spline:
            track = self.get_bone_spline_animation_track(bone, anim_id)
            rot = QuatTransform(rotation=rotation)
            track.apply_transform_to_translate(rot)
            track.apply_transform_to_rotation(rot)
        elif animation.is_interleaved:
            transforms = self.get_bone_interleaved_transforms(bone, anim_id)
            for transform in transforms:
                transform.translate = rotation.apply_to_vector(transform.translate)
                transform.rotation = rotation * transform.rotation
        else:
            raise TypeError("Can only rotate bone tracks for spline or interleaved animations.")

    def auto_retarget_interleaved_animation(
        self,
        source_manager: BaseAnimationManager,
        source_anim_id: int,
        dest_anim_id: int,
        bone_name_mapping: dict[str, str | None | list[str]],
    ):
        """Read `source_anim_id` from `source_manager` and use `bone_name_mapping` to convert the animation tracks to
        `new_anim_id` in this manager.

        `bone_name_mapping` should map the names of bones in THIS skeleton to those in `source_manager`'s skeleton.
        """
        source_animation = source_manager.get_animation(source_anim_id)
        dest_animation = self.get_animation(dest_anim_id)
        source_animation.load_interleaved_data()
        dest_animation.load_interleaved_data()

        frame_count = source_animation.frame_count
        new_frames = [[] for _ in range(frame_count)]  # type: list[list[QuatTransform]]
        for i, bone in enumerate(self.skeleton.bones):
            try:
                source_bone = bone_name_mapping[bone.name]
            except KeyError:
                raise KeyError(f"Target skeleton bone '{bone.name}' has no key in mapping to source bone names.")
            if source_bone is None:
                # Bone has no corresponding bone in source skeleton. We default to the bone's reference pose (T-pose).
                bone_qs_transform = self.skeleton.skeleton.referencePose[i]
                for frame in new_frames:
                    frame.append(bone_qs_transform.to_quat_transform())  # fresh object for each frame
                _LOGGER.info(f"Using default reference pose for unmapped bone '{bone.name}'.")
            elif isinstance(source_bone, (list, tuple)):
                if not source_animation.is_interleaved:
                    raise TypeError("Source animation must be interleaved to compose multiple bones in retarget.")
                if not dest_animation.is_interleaved:
                    raise TypeError("Dest animation must be interleaved to get multiple composed bones in retarget.")

                for frame in new_frames:
                    frame.append(QuatTransform.identity())
                for component_bone_name in reversed(source_bone):  # rightmost bone first (most childish)
                    if component_bone_name.startswith("~"):
                        component_bone_name = component_bone_name[1:]
                        invert = True
                    else:
                        invert = False
                    component_transforms = source_manager.get_bone_interleaved_transforms(
                        component_bone_name, source_anim_id
                    )
                    for frame, component_t in zip(new_frames, component_transforms):
                        if invert:
                            frame[-1] = component_t.inverse_mul(frame[-1])
                        else:
                            frame[-1] = component_t @ frame[-1]

                _LOGGER.info(f"Bone '{bone.name}' mapped to composed source bones: {source_bone}")
            else:
                _LOGGER.info(f"Bone '{bone.name}' mapped to source bone '{source_bone}'.")
                bone_transforms = source_manager.get_bone_interleaved_transforms(source_bone, source_anim_id)
                for frame, bone_t in zip(new_frames, bone_transforms):
                    frame.append(bone_t)

        dest_animation.interleaved_data = new_frames

        # Copy over root motion (modify list in place).
        try:
            source_reference_frame_samples = source_animation.get_reference_frame_samples()
        except TypeError:
            try:
                dest_animation.set_reference_frame_samples([])  # TODO: may be the wrong thing to do
                _LOGGER.info("Cleared animation reference frame samples during retarget.")
            except TypeError:
                pass
        else:
            dest_animation.set_reference_frame_samples(source_reference_frame_samples)
            _LOGGER.info("Retargeted animation reference frame samples.")

        _LOGGER.info(f"Auto-retarget complete. Animation {dest_anim_id} saved.")

    def auto_retarget_spline_animation(
        self,
        source_manager: BaseAnimationManager,
        source_anim_id: int,
        dest_anim_id: int,
        bone_name_mapping: dict[str, str | None | list[str]],
    ):
        """Read `source_anim_id` from `source_manager` and use `bone_name_mapping` to convert the animation tracks to
        `new_anim_id` in this manager.

        `bone_name_mapping` should map the names of bones in THIS skeleton to those in `source_manager`'s skeleton.
        """
        source_animation = source_manager.get_animation(source_anim_id)
        dest_animation = self.get_animation(dest_anim_id)
        source_animation.load_spline_data()
        dest_animation.load_spline_data()

        new_block = []  # type: list[SplineTransformTrack]
        for i, bone in enumerate(self.skeleton.bones):
            try:
                source_bone_name = bone_name_mapping[bone.name]
            except KeyError:
                raise KeyError(f"Target skeleton bone '{bone.name}' has no key in mapping to source bone names.")
            if source_bone_name is None:
                # Bone has no corresponding bone in source skeleton. We default to the bone's reference pose (T-pose).
                static_track = self._get_tpose_spline_transform_track(bone_index=i)
                new_block.append(static_track)
                _LOGGER.info(f"Using default reference pose for unmapped bone '{bone.name}'.")
            elif isinstance(source_bone_name, (list, tuple)):
                raise TypeError(
                    "Cannot compose retargeting bones for spline-compressed animations. Convert to interleaved first."
                )
            else:
                _LOGGER.info(f"Bone '{bone.name}' mapped to source bone '{source_bone_name}'.")
                source_track = source_manager.get_bone_spline_animation_track(source_bone_name, source_anim_id)
                new_block.append(copy.deepcopy(source_track))

        dest_animation.spline_data.blocks[0] = new_block

        # Copy over root motion (modify list in place).
        try:
            source_reference_frame_samples = source_animation.get_reference_frame_samples()
        except TypeError:
            try:
                dest_animation.set_reference_frame_samples([])  # TODO: may be the wrong thing to do
                _LOGGER.info("Cleared animation reference frame samples during retarget.")
            except TypeError:
                pass
        else:
            dest_animation.set_reference_frame_samples(source_reference_frame_samples)
            _LOGGER.info("Retargeted animation reference frame samples.")

        _LOGGER.info(f"Auto-retarget complete. Animation {dest_anim_id} saved.")

    def _get_tpose_spline_transform_track(self, bone_index: int) -> SplineTransformTrack:
        bone_qs_transform = self.skeleton.skeleton.referencePose[bone_index]
        return SplineTransformTrack.from_static_transform(
            bone_qs_transform.translation,
            bone_qs_transform.rotation,
            bone_qs_transform.scale,
        )

    def _get_tpose_transform_list(self, bone_index: int, frame_count: int) -> list[QuatTransform]:
        bone_qs_transform = self.skeleton.skeleton.referencePose[bone_index]
        return [bone_qs_transform.to_quat_transform() for _ in range(frame_count)]

    def get_bone_spline_animation_track(self, bone: BONE_SPEC_TYPING, anim_id: int = None) -> SplineTransformTrack:
        bone = self.skeleton.resolve_bone_spec(bone)
        animation = self.get_animation(anim_id)
        if not animation.is_spline:
            raise TypeError("Can only get bone animation tracks for spline-compressed animation.")
        animation.load_spline_data()
        bone_index = self.skeleton.get_bone_index(bone)
        mapping = animation.animation_binding.transformTrackToBoneIndices
        track_index = mapping.index(bone_index)
        return animation.spline_data.blocks[0][track_index]

    def get_immediate_child_bone_spline_animation_tracks(
        self, parent_bone: BONE_SPEC_TYPING, anim_id: int = None
    ) -> list[tuple[int, SplineTransformTrack]]:
        """Get a list of `(int, track)` tuples for all immediate child bones of `parent_bone_name_or_index`."""
        parent_bone = self.skeleton.resolve_bone_spec(parent_bone)
        animation = self.get_animation(anim_id)
        if not animation.is_spline:
            raise TypeError("Can only get bone animation tracks for spline-compressed animation.")
        animation.load_spline_data()
        child_bone_indices = self.skeleton.get_immediate_bone_children_indices(parent_bone)
        mapping = animation.animation_binding.transformTrackToBoneIndices
        child_track_indices = [mapping.index(bone_index) for bone_index in child_bone_indices]
        block = animation.spline_data.blocks[0]
        return [(i, block[i]) for i in child_track_indices]

    def get_bone_interleaved_transforms(
        self, bone: BONE_SPEC_TYPING, anim_id: int = None
    ) -> list[QuatTransform]:
        bone = self.skeleton.resolve_bone_spec(bone)
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        animation.load_interleaved_data()
        bone_index = self.skeleton.get_bone_index(bone)
        mapping = animation.animation_binding.transformTrackToBoneIndices
        track_index = mapping.index(bone_index)
        return [frame[track_index] for frame in animation.interleaved_data]

    def get_immediate_child_bone_interleaved_animation_transforms(
        self, parent_bone: BONE_SPEC_TYPING, anim_id: int = None
    ) -> list[tuple[int, list[QuatTransform]]]:
        """Get a list of `(int, track)` tuples for all immediate child bones of `parent_bone_name_or_index`."""
        parent_bone = self.skeleton.resolve_bone_spec(parent_bone)
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        animation.load_interleaved_data()
        child_bone_indices = self.skeleton.get_immediate_bone_children_indices(parent_bone)
        mapping = animation.animation_binding.transformTrackToBoneIndices
        child_track_indices = [mapping.index(bone_index) for bone_index in child_bone_indices]
        child_index_transforms = []
        for child_index in child_track_indices:
            child_index_transforms.append(
                (child_index, [frame[child_index] for frame in animation.interleaved_data]),
            )
        return child_index_transforms

    # region Read/Write Methods
    @classmethod
    def from_anibnd(cls, anibnd_source: GameFile.Typing, *animation_ids: int, from_bak=False, compendium_name=""):
        anibnd = Binder(anibnd_source, from_bak=from_bak)
        compendium, compendium_name = cls.ANIMATION_HKX.get_compendium_from_binder(anibnd, compendium_name)
        try:
            skeleton = cls.SKELETON_HKX(
                anibnd.find_entry_matching_name(r"[Ss]keleton\.[HKX|hkx]"), compendium=compendium
            )
            animations = {
                anim_id: cls.ANIMATION_HKX(anibnd[cls.animation_id_to_entry_basename(anim_id)], compendium=compendium)
                for anim_id in animation_ids
            }
        except MissingCompendiumError:
            if compendium_name != "":
                raise MissingCompendiumError(
                    f"Binder HKX entry requires a compendium, but compendium '{compendium_name}' "
                    f"could not be found in given binder. Use `compendium_name` argument if it has another name."
                )
            raise MissingCompendiumError(
                f"Binder HKX entry requires a compendium, but `compendium_name` was not given and a "
                f"'.compendium' entry could not be found in the given binder."
            )

        return cls(skeleton, animations)

    def write_anim_ids_into_anibnd(
        self, anibnd_path: Path | str, *anim_ids: int, from_bak=False, write_path: Path | str = None
    ):
        anibnd = Binder(anibnd_path, from_bak=from_bak)
        for anim_id in anim_ids:
            animation = self.animations[anim_id]
            anibnd[self.animation_id_to_entry_basename(anim_id)].set_uncompressed_data(animation.pack_dcx())
        if write_path is None:
            write_path = anibnd_path
        anibnd.write(file_path=write_path)  # will default to same path
        if write_path != anibnd_path:
            _LOGGER.info(f"Animations {', '.join(str(x) for x in anim_ids)} written to {anibnd_path} at {write_path}.")
        else:
            _LOGGER.info(f"Animations {', '.join(str(x) for x in anim_ids)} written into {anibnd_path}.")

    def write_all_into_anibnd(self, anibnd_path: Path | str, from_bak=False, write_path: Path | str = None):
        anibnd = Binder(anibnd_path, from_bak=from_bak)
        anibnd.find_entry_matching_name(r"[Ss]keleton\.[HKX|hkx]").set_uncompressed_data(self.skeleton.pack_dcx())
        for anim_id, animation in self.animations.items():
            anibnd[self.animation_id_to_entry_basename(anim_id)].set_uncompressed_data(animation.pack_dcx())
        anibnd.write(file_path=write_path)  # will default to same path
    # endregion

    @staticmethod
    @abc.abstractmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        if animation_id >= 999999:
            raise ValueError("Max animation ID for DS1 is 999999.")
        return f"a{animation_id // 10000:02d}_{animation_id % 10000:04d}.hkx"
