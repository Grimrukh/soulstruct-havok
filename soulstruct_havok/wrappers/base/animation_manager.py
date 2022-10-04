"""Manager class that combines various HKX files to make animation modification easier.

Currently mainly set up for Havok 2015 (for Nightfall/DSR).
"""
from __future__ import annotations

import abc
import copy
import logging
import typing as tp
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

from soulstruct.base.game_file import GameFile
from soulstruct.containers import Binder

from soulstruct_havok.spline_compression import *
from soulstruct_havok.tagfile.unpacker import MissingCompendiumError
from soulstruct_havok.wrappers.base import BaseAnimationHKX, BaseSkeletonHKX
from soulstruct_havok.wrappers.base.skeleton import BONE_SPEC_TYPING
from soulstruct_havok.utilities.maths import Quaternion, QsTransform
from soulstruct_havok.utilities.vispy_window import VispyWindow

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

    def transform_bone_track(
        self,
        bone: BONE_SPEC_TYPING,
        transform: QsTransform,
        anim_id: int = None,
        compensate_child_bones=False,
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
                parent_t.translation = transform.transform_vector(parent_t.translation)
                parent_t.rotation = transform.rotation * parent_t.rotation
            if compensate_child_bones:
                child_tracks = self.get_immediate_child_bone_interleaved_animation_transforms(bone)
                for child_index, child_transforms in child_tracks:
                    for i in range(len(child_transforms)):
                        parent_t = parent_transforms[i]  # in same frame
                        child_t = child_transforms[i]
                        # Enter parent's frame.
                        child_t.translation = parent_t.transform_vector(child_t.translation)
                        child_t.rotation = parent_t.rotation * child_t.rotation
                        # Apply inverse transform.
                        child_t.translation = transform.inverse_transform_vector(child_t.translation)
                        child_t.rotation = transform.rotation.inverse() * child_t.rotation
                        # Exit parent's frame.
                        child_t.translation = parent_t.inverse_transform_vector(child_t.translation)
                        child_t.rotation = parent_t.rotation.inverse() * child_t.rotation

    def rotate_bone_track(self, bone: BONE_SPEC_TYPING, rotation: Quaternion, anim_id: int = None):
        """Apply `rotation` to every control point (or just the static value) of given bone track."""
        animation = self.get_animation(anim_id)
        if animation.is_spline:
            track = self.get_bone_spline_animation_track(bone, anim_id)
            rot = QsTransform(rotation=rotation)
            track.apply_transform_to_translate(rot)
            track.apply_transform_to_rotation(rot)
        elif animation.is_interleaved:
            transforms = self.get_bone_interleaved_transforms(bone, anim_id)
            for transform in transforms:
                transform.translation = rotation.rotate_vector(transform.translation)
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
        new_frames = [[] for _ in range(frame_count)]  # type: list[list[QsTransform]]
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
                # _LOGGER.info(f"Using default reference pose for unmapped bone '{bone.name}'.")
            elif isinstance(source_bone, (list, tuple)):
                if not source_animation.is_interleaved:
                    raise TypeError("Source animation must be interleaved to compose multiple bones in retarget.")
                if not dest_animation.is_interleaved:
                    raise TypeError("Dest animation must be interleaved to get multiple composed bones in retarget.")

                for frame in new_frames:
                    frame.append(QsTransform.identity())
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
                            frame[-1] = component_t.inverse().compose(frame[-1], scale_translation=True)
                        else:
                            frame[-1] = component_t.compose(frame[-1], scale_translation=True)

                # _LOGGER.info(f"Bone '{bone.name}' mapped to composed source bones: {source_bone}")
            else:
                # _LOGGER.info(f"Bone '{bone.name}' mapped to source bone '{source_bone}'.")
                bone_transforms = source_manager.get_bone_interleaved_transforms(source_bone, source_anim_id)
                for frame, bone_t in zip(new_frames, bone_transforms):
                    frame.append(copy.deepcopy(bone_t))  # new object

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
                # _LOGGER.info(f"Using default reference pose for unmapped bone '{bone.name}'.")
            elif isinstance(source_bone_name, (list, tuple)):
                raise TypeError(
                    "Cannot compose retargeting bones for spline-compressed animations. Convert to interleaved first."
                )
            else:
                # _LOGGER.info(f"Bone '{bone.name}' mapped to source bone '{source_bone_name}'.")
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

    def _get_tpose_transform_list(self, bone_index: int, frame_count: int) -> list[QsTransform]:
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
        self, bone: BONE_SPEC_TYPING, anim_id: int = None, use_root_space=False,
    ) -> list[QsTransform]:
        bone = self.skeleton.resolve_bone_spec(bone)
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        animation.load_interleaved_data()
        bone_index = self.skeleton.get_bone_index(bone)
        mapping = animation.animation_binding.transformTrackToBoneIndices
        track_index = mapping.index(bone_index)
        transforms = [frame[track_index] for frame in animation.interleaved_data]

        if not use_root_space:
            return transforms  # local transforms suffice

        # Compose transforms with all parents.
        frame_count = len(transforms)
        hierarchy = self.skeleton.get_hierarchy_to_bone(bone)
        for parent in reversed(hierarchy[:-1]):  # exclude this bone (already retrieved) and reverse order
            parent_transforms = self.get_bone_interleaved_transforms(parent)
            for i in range(frame_count):
                transforms[i] = parent_transforms[i].compose(transforms[i], scale_translation=True)
        return transforms

    def get_all_interleaved_bone_transforms_at_frame(self, frame: int, anim_id: int = None) -> list[QsTransform]:
        """Resolve all transforms to get root space transforms at the given `frame` index.

        TODO: Lots of redundant calculations right now; it would be more efficient to work my way downward rather than
         upward from each bone.
        """
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        animation.load_interleaved_data()
        if frame > len(animation.interleaved_data):
            raise ValueError(f"Frame must be between 0 and {len(animation.interleaved_data)}, not {frame}.")
        all_bone_index_hierarchies = self.skeleton.get_all_bone_parent_indices()
        frame_transforms = animation.interleaved_data[frame]
        # NOTE: `root_transforms` is ordered by bone, not track. Bones without tracks will have identity transforms.
        root_transforms = [QsTransform.identity() for _ in self.skeleton.bones]
        mapping = animation.animation_binding.transformTrackToBoneIndices
        for track_index, bone_index in enumerate(mapping):
            bone_index_hierarchy = all_bone_index_hierarchies[bone_index]
            for parent_index in reversed(bone_index_hierarchy):  # start with own local transform and work way upward
                parent_transform = frame_transforms[mapping.index(parent_index)]
                root_transforms[bone_index] = parent_transform @ root_transforms[bone_index]  # scales translation
        return root_transforms

    def get_immediate_child_bone_interleaved_animation_transforms(
        self, parent_bone: BONE_SPEC_TYPING, anim_id: int = None
    ) -> list[tuple[int, list[QsTransform]]]:
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

    def plot_tpose_skeleton(
        self,
        bone_names=(),
        scale=1.0,
        window=None,
        scatter_color="blue",
        line_color="white",
        label_bones=True,
    ):
        """Figure out how to properly resolve bones in a nice way, with connected heads and tails, for Blender."""
        # noinspection PyPackageRequirements
        # Even if only some `bone_names` are given, we collect all of them to draw connective lines from parents.
        bone_translations = [
            scale * self.skeleton.get_bone_root_transform(bone).translation
            for bone in self.skeleton.bones
        ]

        if not bone_names:
            bone_names = [bone.name for bone in self.skeleton.bones]

        if window is None:
            window = VispyWindow()

        points = []
        lines = []
        for bone_name in bone_names:
            bone = self.skeleton.resolve_bone_spec(bone_name)
            bone_index = self.skeleton.bones.index(bone)
            translation = bone_translations[bone_index]
            points.append(translation.to_xzy())

            parent_index = self.skeleton.get_bone_parent_index(bone)
            if parent_index != -1:
                parent_translation = bone_translations[parent_index]
                lines.append(np.array([parent_translation.to_xzy(), translation.to_xzy()]))

        window.add_markers(np.array(points), face_color=scatter_color)
        for line in lines:
            window.add_line(line, line_color=line_color)

        return window

    def plot_interleaved_skeleton_on_frame(
        self,
        frame: int,
        anim_id: int = None,
        window=None,
        scatter_color="blue",
        line_color="white",
        label_bones=True,
        label_bone_filter="",
    ):
        """Plot every bone on the given frame of the given animation."""
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only plot interleaved animations.")
        animation.load_interleaved_data()
        root_transforms = self.get_all_interleaved_bone_transforms_at_frame(frame, anim_id)

        if window is None:
            window = VispyWindow()

        points = []
        lines = []
        for bone_index, bone_root_transform in enumerate(root_transforms):
            bone = self.skeleton.resolve_bone_spec(bone_index)
            translation = bone_root_transform.translation
            points.append(translation.to_xzy())
            # if label_bones and (not label_bone_filter or label_bone_filter in bone.name):
            #     ax.text(translation[0], translation[2], translation[1], f"({bone_index}) {bone.name}")

            parent_index = self.skeleton.get_bone_parent_index(bone)
            if parent_index != -1:
                parent_translation = root_transforms[parent_index].translation
                lines.append(np.array([parent_translation.to_xzy(), translation.to_xzy()]))

        window.add_markers(np.array(points), face_color=scatter_color)
        for line in lines:
            window.add_line(line, line_color=line_color)
        window.add_gridlines()

        return window

    def plot_interleaved_translation(
        self,
        bone: BONE_SPEC_TYPING,
        coord: str,
        anim_id: int = None,
        title: str = None,
        color=None,
        legend=False,
        ylim=None,
        show=False,
        axes=None,
    ):
        """Plot interleaved animation transforms (translation only) in both local bone space and root space."""
        if coord not in ("x", "y", "z"):
            raise ValueError("Coord should be 'x', 'y', or 'z'.")
        bone = self.skeleton.resolve_bone_spec(bone)
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only plot interleaved animations.")
        animation.load_interleaved_data()
        if title is None:
            title = bone.name
        if axes is None:
            fig, axes = plt.subplots(ncols=2, figsize=(10, 5))
            if title:
                fig.suptitle(title)

        for ax, use_root_space in zip(axes, (False, True)):
            transforms = self.get_bone_interleaved_transforms(bone, anim_id, use_root_space=use_root_space)
            values = [getattr(t.translation, coord) for t in transforms]
            ax.plot(values, label=bone.name, color=color)
            if legend and not use_root_space:
                ax.legend()
            if ylim is not None:
                ax.set_ylim(ylim)
        if show:
            plt.show()

    def plot_hierarchy_interleaved_translation(
        self, bone: BONE_SPEC_TYPING, coord: str, anim_id: int = None, title: str = None, ylim=None, show=False
    ):
        """Plot a grid for all bones in the hierarchy up to `bone`, including itself."""
        bone = self.skeleton.resolve_bone_spec(bone)
        hierarchy = self.skeleton.get_hierarchy_to_bone(bone)
        fig, axes = plt.subplots(ncols=2, figsize=(10, 5))
        if title is None:
            title = f"{bone.name} Hierarchy"
        fig.suptitle(title)
        fig.tight_layout()
        inferno = cm.get_cmap("inferno")
        for i, parent_bone in enumerate(hierarchy):
            color = inferno(i / len(hierarchy))
            color = (color[0], color[1], color[2], color[3] * 0.8)
            self.plot_interleaved_translation(
                parent_bone, coord, anim_id, color=color, show=False, axes=axes, ylim=ylim, legend=False
            )
        axes[0].legend()
        if show:
            plt.show()

    @staticmethod
    @abc.abstractmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        ...
