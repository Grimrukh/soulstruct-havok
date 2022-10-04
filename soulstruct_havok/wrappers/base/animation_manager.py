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
from soulstruct_havok.wrappers.base.skeleton import BONE_SPEC_TYPING, BONE_TYPING
from soulstruct_havok.utilities.maths import Quaternion, TRSTransform, Vector3
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
        transform: TRSTransform,
        anim_id: int = None,
        compensate_child_bones=False,
        affect_translation=True,
        affect_rotation=True,
        affect_parent_rotation=False,
        rotation_orbits_child: BONE_SPEC_TYPING = None,
    ):
        """Apply `transform` to every control point or static transform in the given bone's track.

        If `compensate_child_bones=True`, the all tracks of the bone's immediate children will be counter-transformed in
        such a way that they do not move relative to this parent bone, which is useful for IK. The animation must be
        interleaved to do this, as synchonized parent-child data is needed for each frame (and I can't unpack, edit,
        and regenerate splines myself).
        """
        if not affect_translation and not affect_rotation:
            raise ValueError("At least one of `affect_translation` or `affect_rotation` must be True!")
        if rotation_orbits_child and affect_rotation:
            raise ValueError("Cannot set `rotation_orbits_child` when `affect_rotation=True`.")
        if affect_rotation and affect_parent_rotation:
            _LOGGER.warning(
                "Transforming bone with `affect_rotation` and `affect_parent_rotation` both True! This is unusual."
            )
        bone = self.skeleton.resolve_bone_spec(bone)
        animation = self.get_animation(anim_id)
        if animation.is_spline:
            track = self.get_bone_spline_animation_track(bone, anim_id)
            if affect_translation:
                track.apply_transform_to_translate(transform)
            if affect_rotation:
                track.apply_transform_to_rotation(transform)
            if compensate_child_bones:
                raise ValueError("Cannot use `fix_children=True` for a spline-compressed animation.")
        elif animation.is_interleaved:
            transforms = self.get_bone_interleaved_transforms(bone, anim_id)
            pre_change_target_t = None
            if rotation_orbits_child:
                target_child_transforms = self.get_bone_interleaved_transforms(
                    rotation_orbits_child, anim_id
                )
            else:
                target_child_transforms = None

            for i, this_t in enumerate(transforms):
                if rotation_orbits_child:
                    pre_change_target_t = this_t.transform_vector(target_child_transforms[i].translation)
                if affect_translation:
                    this_t.translation = transform.transform_vector(this_t.translation)
                if rotation_orbits_child:
                    post_change_target_t = this_t.transform_vector(target_child_transforms[i].translation)
                    preserving_rotation = Quaternion.from_vector_change(pre_change_target_t, post_change_target_t)
                    this_t.rotation = preserving_rotation * this_t.rotation
                    affect_rotation = True  # trigger child rotation compensation below
                elif affect_rotation:
                    this_t.rotation = transform.rotation * this_t.rotation

            if affect_parent_rotation and (parent_bone := self.skeleton.get_bone_parent(bone)):
                parent_transforms = self.get_bone_interleaved_transforms(parent_bone, anim_id)

            if compensate_child_bones:
                child_tracks = self.get_immediate_child_bone_interleaved_animation_transforms(bone)
                for child_index, child_transforms in child_tracks:
                    for i in range(len(child_transforms)):
                        this_t = transforms[i]  # in same frame
                        child_t = child_transforms[i]
                        # Enter parent's frame, apply inverse transform, then exit parent's frame.
                        if affect_translation:
                            child_t.translation = this_t.transform_vector(child_t.translation)
                            child_t.translation = transform.inverse_transform_vector(child_t.translation)
                            child_t.translation = this_t.inverse_transform_vector(child_t.translation)
                        if affect_rotation:
                            child_t.rotation = this_t.rotation * child_t.rotation
                            child_t.rotation = transform.rotation.inverse() * child_t.rotation
                            child_t.rotation = this_t.rotation.inverse() * child_t.rotation

    def rotate_bone_track(
        self,
        bone: BONE_SPEC_TYPING,
        rotation: Quaternion | list[Quaternion],
        anim_id: int = None,
        compensate_children=False,
    ):
        """Apply `rotation` to `bone.rotation` in every animation frame. Requires interleaved animation.

        If `compensate_children=True` (NOT default), children of `bone` will be transformed in a way that preserves
        their transforms relative to root space.
        """
        bone = self.skeleton.resolve_bone_spec(bone)
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only use `proper_transform_bone_track()` for interleaved animations.")
        bone_tfs = self.get_bone_interleaved_transforms(bone, anim_id)

        if isinstance(rotation, (list, tuple)) and len(rotation) != len(bone_tfs):
            raise ValueError(f"Received a list of {len(rotation)} rotations, but there are {len(bone_tfs)} frames.")

        print(f"Rotating frame of bone {bone.name}.")

        all_child_tfs = []
        all_initial_root_child_tfs = []  # copied grandparent-space child transforms
        if compensate_children:
            # Get local child transforms (direct object references).
            all_child_bones_tfs = self.get_immediate_child_bone_interleaved_animation_transforms(bone)
            # Store initial transforms of all immediate children relative to grandparent (as parent rotation may be
            # changed). Parent bone is guaranteed to exist per the check above.
            for child_bone, child_tfs in all_child_bones_tfs:
                all_child_tfs.append(child_tfs)

                root_child_tfs = []
                for bone_tf, child_tf in zip(bone_tfs, child_tfs):
                    root_child_tf = copy.deepcopy(child_tf)
                    root_child_tf.translation = bone_tf.transform_vector(child_tf.translation)
                    root_child_tf.rotation = bone_tf.rotation * child_tf.rotation
                    # We don't care about storing the child's scale (this function will never affect it).
                    root_child_tfs.append(root_child_tf)

                all_initial_root_child_tfs.append(root_child_tfs)

        for i, bone_tf in enumerate(bone_tfs):
            # Modify `bone_tf.rotation` directly from `transform.rotation`, as it is not orbiting a child.
            if isinstance(rotation, (list, tuple)):
                bone_tf.left_multiply_rotation(rotation[i])
            else:
                bone_tf.left_multiply_rotation(rotation)

        # We still compensate the target along with any other non-target children below. (Because the main
        # bone is already pointing toward the old "root" translation of the target child, that particular
        # child will only need to be further compensated with some amount of scaling, in practice.)

        if compensate_children:
            for initial_root_child_tfs, child_tfs in zip(all_initial_root_child_tfs, all_child_tfs):
                for i, (initial_root_child_tf, child_tf, bone_tf) in enumerate(
                    zip(initial_root_child_tfs, child_tfs, bone_tfs)
                ):
                    initial_root_trans = initial_root_child_tf.translation
                    child_tf.translation = bone_tf.inverse_transform_vector(initial_root_trans)
                    initial_root_rot = initial_root_child_tf.rotation
                    child_tf.rotation = bone_tf.rotation.inverse() * initial_root_rot

    def proper_transform_bone_track(
        self,
        bone: BONE_SPEC_TYPING,
        transform: TRSTransform,
        anim_id: int = None,
        rotate_parent=True,
        compensate_children=False,
        rotation_orbits_child: BONE_SPEC_TYPING = None,
    ):
        """Apply `transform` to every animation frame for `bone`. Depending on usage, may also affect local parent and
        child transforms. Requires interleaved animation.

        If `rotate_parent=True` (default), the transform's rotation will be applied to the parent of the target bone
        rather than itself, which will preserve relative bone orientation for meshes.

        If `compensate_children=True` (NOT default), children of `bone` will be transformed in a way that preserves
        their transforms relative to root space (not necessarily only relative to the parent of `bone`, which could
        rotate).

        If `rotation_orbits_child` is set to a bone (which must be a child of `bone`), the rotation of
        `bone` will be compensated to preserve its orientation relative to that child. Cannot be used with
        `rotate_parent=False`.
        """
        if rotation_orbits_child and not compensate_children:
            raise ValueError(
                "Cannot set `rotation_orbits_child` when `compensate_children=False`. Relative rotation "
                "will naturally be preserved (local child transforms will not change)."
            )
        bone = self.skeleton.resolve_bone_spec(bone)
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only use `proper_transform_bone_track()` for interleaved animations.")
        bone_tfs = self.get_bone_interleaved_transforms(bone, anim_id)

        if isinstance(transform, (list, tuple)) and len(transform) != len(bone_tfs):
            raise ValueError(f"Received a list of {len(transform)} transforms, but there are {len(bone_tfs)} frames.")

        parent_bone = self.skeleton.get_bone_parent(bone)
        if parent_bone is None and (rotate_parent or compensate_children):
            raise ValueError(
                f"Bone '{bone.name}' has no parent. You must set `rotate_parent=False` and `compensate_children=False`."
            )
        parent_tfs = self.get_bone_interleaved_transforms(parent_bone, anim_id)

        print(f"Transforming bone {bone.name} with reference to parent {parent_bone.name}.")

        target_bone = None
        target_bone_tfs = []
        initial_root_target_tfs = []
        if rotation_orbits_child:
            target_bone = self.skeleton.resolve_bone_spec(rotation_orbits_child)
            if self.skeleton.get_bone_parent(target_bone) is not bone:
                raise ValueError(
                    f"Bone '{target_bone.name}' (`rotation_orbits_child` target) is not a child of "
                    f"transforming bone '{bone.name}'."
                )

        all_child_tfs = []
        all_initial_root_child_tfs = []  # copied grandparent-space child transforms
        if compensate_children:
            # Get local child transforms (direct object references).
            all_child_bones_tfs = self.get_immediate_child_bone_interleaved_animation_transforms(bone)
            # Store initial transforms of all immediate children relative to grandparent (as parent rotation may be
            # changed). Parent bone is guaranteed to exist per the check above.
            for child_bone, child_tfs in all_child_bones_tfs:
                all_child_tfs.append(child_tfs)

                if target_bone and child_bone is target_bone:
                    target_bone_tfs = child_tfs  # store separately for convenience

                root_child_tfs = []
                for parent_tf, bone_tf, child_tf in zip(parent_tfs, bone_tfs, child_tfs):
                    root_child_tf = copy.deepcopy(child_tf)
                    root_child_tf.translation = (parent_tf @ bone_tf).transform_vector(child_tf.translation)
                    root_child_tf.rotation = (parent_tf @ bone_tf).rotation * child_tf.rotation
                    # We don't care about storing the child's scale (this function will never affect it).
                    root_child_tfs.append(root_child_tf)

                all_initial_root_child_tfs.append(root_child_tfs)

                if target_bone and child_bone is target_bone:
                    initial_root_target_tfs = root_child_tfs  # store separately for convenience

        for i, (parent_tf, bone_tf) in enumerate(zip(parent_tfs, bone_tfs)):
            if rotate_parent:
                # Modify translation using scale/translation components of transform, but apply rotation only to parent.
                bone_tf.translation = transform.scale * bone_tf.translation + transform.translation
                parent_tf.left_multiply_rotation(transform.rotation)

                if target_bone:
                    # Compensate `bone_tf.rotation` to point toward OLD absolute target child position.
                    # TODO: I'm sure there's a way to calculate the new `bone_tf.rotation` directly, but I can't think
                    #  of it right now. If this works, I'm leaving it for the time being.
                    initial_translation = parent_tf.inverse_transform_vector(
                        initial_root_target_tfs[i].translation
                    ) - bone_tf.translation  # in parent space, but relative to new bone translation
                    new_translation = bone_tf.transform_vector(target_bone_tfs[i].translation) - bone_tf.translation

                    compensating_rotation = Quaternion.from_vector_change(
                        new_translation.normalize(),
                        initial_translation.normalize(),
                    )

                    bone_tf.left_multiply_rotation(compensating_rotation)
            else:
                # Scale, rotate, and translate bone translation directly.
                bone_tf.translation = transform.transform_vector(bone_tf.translation)

                if target_bone:
                    # Compensate `bone_tf.rotation` to point toward OLD absolute target child position.
                    # TODO: I'm sure there's a way to calculate the new `bone_tf.rotation` directly, but I can't think
                    #  of it right now. If this works, I'm leaving it for the time being.
                    initial_translation = parent_tf.inverse_transform_vector(
                        initial_root_target_tfs[i].translation
                    ) - bone_tf.translation  # in parent space, but relative to new bone translation
                    new_translation = bone_tf.transform_vector(target_bone_tfs[i].translation) - bone_tf.translation

                    compensating_rotation = Quaternion.from_vector_change(
                        new_translation.normalize(),
                        initial_translation.normalize(),
                    )

                    bone_tf.left_multiply_rotation(compensating_rotation)
                else:
                    # Modify `bone_tf.rotation` directly from `transform.rotation`, as it is not orbiting a child.
                    bone_tf.left_multiply_rotation(transform.rotation)

        # We still compensate the target along with any other non-target children below. (Because the main
        # bone is already pointing toward the old "root" translation of the target child, that particular
        # child will only need to be further compensated with some amount of scaling, in practice.)

        if compensate_children:
            for initial_root_child_tfs, child_tfs in zip(all_initial_root_child_tfs, all_child_tfs):
                for i, (initial_root_child_tf, child_tf, parent_tf, bone_tf) in enumerate(zip(
                    initial_root_child_tfs, child_tfs, parent_tfs, bone_tfs
                )):
                    initial_root_trans = initial_root_child_tf.translation
                    child_tf.translation = (parent_tf @ bone_tf).inverse_transform_vector(initial_root_trans)
                    initial_root_rot = initial_root_child_tf.rotation
                    child_tf.rotation = (parent_tf.rotation * bone_tf.rotation).inverse() * initial_root_rot

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
        new_frames = [[] for _ in range(frame_count)]  # type: list[list[TRSTransform]]
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
                    frame.append(TRSTransform.identity())
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

    def _get_tpose_transform_list(self, bone_index: int, frame_count: int) -> list[TRSTransform]:
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
    ) -> list[TRSTransform]:
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

    def get_all_interleaved_bone_transforms_at_frame(self, frame: int, anim_id: int = None) -> list[TRSTransform]:
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
        root_transforms = [TRSTransform.identity() for _ in self.skeleton.bones]
        mapping = animation.animation_binding.transformTrackToBoneIndices
        for track_index, bone_index in enumerate(mapping):
            bone_index_hierarchy = all_bone_index_hierarchies[bone_index]
            for parent_index in reversed(bone_index_hierarchy):  # start with own local transform and work way upward
                parent_transform = frame_transforms[mapping.index(parent_index)]
                root_transforms[bone_index] = parent_transform @ root_transforms[bone_index]  # scales translation
        return root_transforms

    def get_immediate_child_bone_interleaved_animation_transforms(
        self, parent_bone: BONE_SPEC_TYPING, anim_id: int = None
    ) -> list[tuple[BONE_TYPING, list[TRSTransform]]]:
        """Get a list of `(int, track)` tuples for all immediate child bones of `parent_bone_name_or_index`."""
        parent_bone = self.skeleton.resolve_bone_spec(parent_bone)
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        animation.load_interleaved_data()
        child_bone_indices = self.skeleton.get_immediate_bone_children_indices(parent_bone)
        mapping = animation.animation_binding.transformTrackToBoneIndices
        child_track_indices = [mapping.index(bone_index) for bone_index in child_bone_indices]
        child_bones_and_transforms = []
        for child_index in child_track_indices:
            child_bones_and_transforms.append(
                (
                    self.skeleton.resolve_bone_spec(child_index),
                    [frame[child_index] for frame in animation.interleaved_data],
                ),
            )
        return child_bones_and_transforms

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
        focus_bone=None,
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
        line_points = []
        x_arrow_line_points = []
        x_arrows = []
        z_arrow_line_points = []
        z_arrows = []
        for bone_index, bone_root_transform in enumerate(root_transforms):
            bone = self.skeleton.resolve_bone_spec(bone_index)
            translation = bone_root_transform.translation.to_xzy()
            points.append(translation)
            # if label_bones and (not label_bone_filter or label_bone_filter in bone.name):
            #     ax.text(translation[0], translation[2], translation[1], f"({bone_index}) {bone.name}")

            parent_index = self.skeleton.get_bone_parent_index(bone)
            if parent_index != -1:
                parent_translation = root_transforms[parent_index].translation
                line_points += [parent_translation.to_xzy(), translation]

            # Draw axes along X (red) and Z (green) axes.
            rotation = bone_root_transform.rotation
            x_end = (bone_root_transform.translation + rotation.rotate_vector(Vector3(0.1, 0, 0))).to_xzy()  # X
            z_end = (bone_root_transform.translation + rotation.rotate_vector(Vector3(0, 0, 0.1))).to_xzy()  # Z

            x_arrow_line_points += [translation, x_end]
            z_arrow_line_points += [translation, z_end]
            x_arrows += [x_end, 0.9 * x_end]
            z_arrows += [z_end, 0.9 * z_end]

            if bone.name == focus_bone:
                window.set_camera_center(translation)

        window.add_markers(np.array(points), face_color=scatter_color)
        window.add_line(np.array(line_points), line_color=line_color, connect="segments")
        window.add_arrow(np.array(x_arrow_line_points), arrows=np.array(x_arrows), connect="segments", color="red")
        window.add_arrow(np.array(z_arrow_line_points), arrows=np.array(z_arrows), connect="segments", color="green")
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
        if coord not in ("x", "y", "z", "magnitude"):
            raise ValueError("Coord should be 'x', 'y', 'z', or 'magnitude'.")
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
            if coord in ("x", "y", "z"):
                values = [getattr(t.translation, coord) for t in transforms]
            else:  # magnitude
                values = [abs(t.translation) for t in transforms]
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
