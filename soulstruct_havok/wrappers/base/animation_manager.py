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
try:
    import matplotlib.pyplot as plt
    from matplotlib import cm
except ModuleNotFoundError:
    plt = cm = None

from soulstruct.base.game_file import GameFile
from soulstruct.containers import Binder

from soulstruct_havok.spline_compression import *
from soulstruct_havok.tagfile.unpacker import MissingCompendiumError
from soulstruct_havok.wrappers.base import BaseAnimationHKX, BaseSkeletonHKX
from soulstruct_havok.wrappers.base.skeleton import BONE_SPEC_TYPING, BONE_TYPING
from soulstruct_havok.utilities.maths import Quaternion, TRSTransform, Vector3

try:
    from soulstruct_havok.utilities.vispy_window import VispyWindow  # could be `None` if `vispy` not installed
except ImportError:
    VispyWindow = None

_LOGGER = logging.getLogger(__name__)


class BaseAnimationManager(abc.ABC):

    ANIMATION_HKX: tp.Type[BaseAnimationHKX]
    SKELETON_HKX: tp.Type[BaseSkeletonHKX]
    skeleton: BaseSkeletonHKX
    animations: dict[int, BaseAnimationHKX]
    default_anim_id: int | None

    # Tracks whether each animation's transforms have been converted to world space with `change_local_to_world()`.
    # If true on pack, transforms will be converted back. They can also be converted with `change_world_to_local()`.
    _is_world_space: dict[int, bool]

    def __init__(self, skeleton: BaseSkeletonHKX, animations: dict[int, BaseAnimationHKX]):
        self.skeleton = skeleton
        self.animations = animations
        if len(animations) == 1:
            self.default_anim_id = list(animations)[0]
        else:
            self.default_anim_id = None  # undecided
        self._is_world_space = {}
        for anim_id in self.animations:
            self._is_world_space[anim_id] = False

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

    def change_local_to_world(self, anim_id: int = None):
        """Convert all animation transforms from their default local coordinates relative to parent to coordinates in
        world space.

        TODO: Currently only supported for interleaved, but could easily be done for splines too by transforming the
         control points.
        """
        animation = self.get_animation(anim_id)
        if anim_id is None:
            anim_id = self.default_anim_id
        if not animation.is_interleaved:
            raise TypeError("Animation must be interleaved to convert to/from world space.")
        if self._is_world_space[anim_id]:
            raise ValueError(f"Animation {anim_id} is already in world space.")
        mapping = animation.animation_binding.transformTrackToBoneIndices

        track_count = animation.track_count
        for track_index in range(track_count):
            bone_index = mapping[track_index]
            parent_indices = self.skeleton.get_bone_ascending_parent_indices(bone_index)
            for frame in animation.interleaved_data:
                for parent_index in parent_indices:
                    frame[bone_index] = frame[parent_index] @ frame[bone_index]

        # `animation.interleaved_data` has now been modified in place (but NOT saved automatically).
        self._is_world_space[anim_id] = True

    def change_world_to_local(self, anim_id: int = None):
        """Convert all animation transforms from world space (done via `change_local_to_world()` back to their standard
        parent-relative spaces.

        TODO: Currently only supported for interleaved, but could easily be done for splines too.
        """
        animation = self.get_animation(anim_id)
        if anim_id is None:
            anim_id = self.default_anim_id
        if not animation.is_interleaved:
            raise TypeError("Animation must be interleaved to convert to/from world space.")
        if not self._is_world_space[anim_id]:
            raise ValueError(f"Animation {anim_id} is already in local space.")
        mapping = animation.animation_binding.transformTrackToBoneIndices

        track_count = animation.track_count
        for track_index in range(track_count):
            bone_index = mapping[track_index]
            parent_indices = self.skeleton.get_bone_descending_parent_indices(bone_index)
            for frame in animation.interleaved_data:
                for parent_index in parent_indices:
                    frame[bone_index] = frame[parent_index].inverse() @ frame[bone_index]

        # `animation.interleaved_data` has now been modified in place (but NOT saved automatically).
        self._is_world_space[anim_id] = False

    def rotate_bone_track(
        self,
        bone: BONE_SPEC_TYPING,
        rotation: Quaternion | list[Quaternion],
        anim_id: int = None,
        compensate_children=False,
    ):
        """Apply `rotation` to `bone.rotation` in every animation frame. Requires interleaved animation.

        If `compensate_children=True` (NOT default), children of `bone` will be transformed in a way that preserves
        their transforms in world space.
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
        all_initial_child_world_tfs = []  # copied grandparent-space child transforms
        if compensate_children:
            # Get local child transforms (direct object references).
            all_child_bones_tfs = self.get_immediate_child_bone_interleaved_animation_transforms(bone)
            # Store initial transforms of all immediate children relative to grandparent (as parent rotation may be
            # changed). Parent bone is guaranteed to exist per the check above.
            for child_bone, child_tfs in all_child_bones_tfs:
                all_child_tfs.append(child_tfs)

                child_world_tfs = []
                for bone_tf, child_tf in zip(bone_tfs, child_tfs):
                    root_child_tf = copy.deepcopy(child_tf)
                    root_child_tf.translation = bone_tf.transform_vector(child_tf.translation)
                    root_child_tf.rotation = bone_tf.rotation * child_tf.rotation
                    # We don't care about storing the child's scale (this function will never affect it).
                    child_world_tfs.append(root_child_tf)

                all_initial_child_world_tfs.append(child_world_tfs)

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
            for initial_root_child_tfs, child_tfs in zip(all_initial_child_world_tfs, all_child_tfs):
                for i, (initial_root_child_tf, child_tf, bone_tf) in enumerate(
                    zip(initial_root_child_tfs, child_tfs, bone_tfs)
                ):
                    initial_root_trans = initial_root_child_tf.translation
                    child_tf.translation = bone_tf.inverse_transform_vector(initial_root_trans)
                    initial_root_rot = initial_root_child_tf.rotation
                    child_tf.rotation = bone_tf.rotation.inverse() * initial_root_rot

    def swivel_bone_track(
        self,
        parent_bone: BONE_SPEC_TYPING,
        swiveling_bone: BONE_SPEC_TYPING,
        child_bone: BONE_SPEC_TYPING,
        angle: float | list[float],
        anim_id: int = None,
        radians=False,
    ):
        """Rotate `parent_bone` in a way that rotates the final position of `swiveling_bone` around the vector from
        `parent_bone` to `child_bone` by `angle` on each frame.

        Useful for rotating bones without changing their length.

        TODO: Doesn't really work; bone rotations are difficult to keep consistent? Or maybe the lengths just get too
         screwed up.

        TODO: I think I know how to fix this now: the rotation needs to be the shortest arc, NOT the swiveling rotation
         itself.
        """
        parent_bone = self.skeleton.resolve_bone_spec(parent_bone)
        swiveling_bone = self.skeleton.resolve_bone_spec(swiveling_bone)
        child_bone = self.skeleton.resolve_bone_spec(child_bone)
        if self.skeleton.get_bone_parent(swiveling_bone) is not parent_bone:
            raise ValueError("Swiveling bone must be an immediate child of parent bone.")
        if self.skeleton.get_bone_parent(child_bone) is not swiveling_bone:
            raise ValueError("Child bone must be an immediate child of swiveling bone.")

        parent_tfs = self.get_bone_interleaved_transforms(parent_bone, anim_id)
        if isinstance(angle, (list, tuple)) and len(angle) != len(parent_tfs):
            raise ValueError(f"Received a list of {len(angle)} swivel angles, but there are {len(parent_tfs)} frames.")
        swiveling_tfs = self.get_bone_interleaved_transforms(swiveling_bone, anim_id)
        child_tfs = self.get_bone_interleaved_transforms(child_bone, anim_id)

        transforms = []
        for i, (parent_tf, swivel_tf, child_tf) in enumerate(zip(parent_tfs, swiveling_tfs, child_tfs)):
            child_point_from_parent = swivel_tf.transform_vector(child_tf.translation)
            rotation_axis = child_point_from_parent.normalize()  # vector to swivel around
            a = angle[i] if isinstance(angle, (list, tuple)) else angle
            rotation = Quaternion.from_axis_angle(rotation_axis, a, radians=radians)
            transforms.append(TRSTransform(rotation=rotation))

        print(f"Swiveling bone {swiveling_bone.name} between {parent_bone.name} and {child_bone.name}.")

        self.transform_bone_track(
            bone=swiveling_bone,
            transform=transforms,
            anim_id=anim_id,
            rotate_parent=True,
            compensate_children=True,
            rotation_orbits_child=child_bone,
            freeze_rotation=True,
        )

    def transform_bone_track(
        self,
        bone: BONE_SPEC_TYPING,
        transform: TRSTransform | list[TRSTransform],
        anim_id: int = None,
        rotate_parent=True,
        compensate_children=False,
        rotation_orbits_child: BONE_SPEC_TYPING = None,
        freeze_rotation=False,
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

        If `freeze_rotation=True`, and `rotate_parent=True`, the rotation of `bone` relative to its grandparent will be
        preserved even its parent's rotation is modified with `transform.rotation`. If `rotation_orbits_child` is given,
        `bone` will still be rotated to orbit that child.

        TODO: Rotating a bone while compensating its children will, generally, stretch bones. I've tried to make a
         "swivel" function above that avoids this by only permitting rotations around an axis that preserves bone
         lengths, but it seems to cause other twisting issues.
        """
        if rotation_orbits_child and not compensate_children:
            raise ValueError(
                "Cannot set `rotation_orbits_child` when `compensate_children=False`. Relative rotation "
                "will naturally be preserved (local child transforms will not change)."
            )
        if freeze_rotation and not rotate_parent:
            raise ValueError("Can only use `freeze_rotation=True` if `rotate_parent=True`.")
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
            tf = transform[i] if isinstance(transform, (list, tuple)) else transform
            if rotate_parent:
                # Modify translation using scale/translation components of transform, but apply rotation only to parent.
                bone_tf.translation = tf.scale * bone_tf.translation + tf.translation
                # NOTE: we right-multiply the rotation to mimic the effective result of left-multipling the main bone's
                # translation (as when `rotate_parent=False`).
                parent_tf.right_multiply_rotation(tf.rotation)
                if freeze_rotation:
                    # Left-multiply `bone.rotation` with inverse rotation to cancel out effect in "root" space.
                    # Will still be compensated to orbit `target_bone` below, if given.
                    bone_tf.left_multiply_rotation(tf.rotation.inverse())
            else:
                # Scale, rotate, and translate bone translation directly.
                bone_tf.translation = tf.transform_vector(bone_tf.translation)
                if not target_bone:
                    # Modify `bone_tf.rotation` directly from `transform.rotation`, as it is not orbiting a child.
                    bone_tf.left_multiply_rotation(tf.rotation)

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

    def local_to_world_space_on_frame(
        self, frame_index: int, bone: BONE_SPEC_TYPING, point_or_transform: Vector3 | TRSTransform, anim_id: int = None
    ) -> Vector3 | TRSTransform:
        """Convert given point or transform (translation and rotation components only) from the local space of `bone`
        to world space by accumulating and applying all parent transforms on `frame`."""
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise ValueError("Can only do per-frame transformations for interleaved animations.")
        animation_frame = animation.interleaved_data[frame_index]
        if isinstance(point_or_transform, Vector3):
            point = point_or_transform  # type: Vector3
            for parent_index in self.skeleton.get_bone_ascending_parent_indices(bone, include_self=True):
                track_index = animation.get_track_index_of_bone(parent_index)
                point = animation_frame[track_index].transform_vector(point)
            return point
        elif isinstance(point_or_transform, TRSTransform):
            transform = point_or_transform  # type: TRSTransform
            for parent_index in self.skeleton.get_bone_ascending_parent_indices(bone, include_self=True):
                track_index = animation.get_track_index_of_bone(parent_index)
                transform = animation_frame[track_index] @ transform
            return transform
        else:
            raise TypeError("Can only convert Vector3 or TRSTransform.")

    def local_to_world_space_all_frames(
        self, bone: BONE_SPEC_TYPING, point_or_transform: Vector3 | TRSTransform, anim_id: int = None
    ) -> list[Vector3] | list[TRSTransform]:
        """Convert given point or transform (translation and rotation components only) from the local space of `bone`
        to world space by accumulating and applying all parent transforms.

        Returns a full list of new world positions/transforms on every frame.
        """
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise ValueError("Can only do per-frame transformations for interleaved animations.")
        if isinstance(point_or_transform, Vector3):
            point = point_or_transform  # type: Vector3
            world_points = []  # type: list[Vector3]
            for frame in animation.interleaved_data:
                frame_world_point = point.copy()
                for parent_index in self.skeleton.get_bone_ascending_parent_indices(bone, include_self=True):
                    track_index = animation.get_track_index_of_bone(parent_index)
                    frame_world_point = frame[track_index].transform_vector(frame_world_point)
                world_points.append(frame_world_point)
            return world_points
        elif isinstance(point_or_transform, TRSTransform):
            transform = point_or_transform  # type: TRSTransform
            world_transforms = []  # type: list[TRSTransform]
            for frame in animation.interleaved_data:
                frame_world_transform = transform.copy()
                for parent_index in self.skeleton.get_bone_ascending_parent_indices(bone, include_self=True):
                    track_index = animation.get_track_index_of_bone(parent_index)
                    frame_world_transform = frame[track_index] @ frame_world_transform
                world_transforms.append(frame_world_transform)
            return world_transforms
        else:
            raise TypeError("Can only convert Vector3 or TRSTransform.")

    def world_to_local_space_on_frame(
        self, frame: int, bone: BONE_SPEC_TYPING, point_or_transform: Vector3 | TRSTransform, anim_id: int = None
    ) -> Vector3 | TRSTransform:
        """Convert given point or transform (translation and rotation components only) from world space to the local
        space of `bone` by accumulating and applying all inverse parent transforms on `frame`."""
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise ValueError("Can only do per-frame transformations for interleaved animations.")
        animation_frame = animation.interleaved_data[frame]
        if isinstance(point_or_transform, Vector3):
            point = point_or_transform  # type: Vector3
            for parent_index in self.skeleton.get_bone_descending_parent_indices(bone, include_self=True):
                track_index = animation.get_track_index_of_bone(parent_index)
                point = animation_frame[track_index].inverse_transform_vector(point)
            return point
        elif isinstance(point_or_transform, TRSTransform):
            transform = point_or_transform  # type: TRSTransform
            for parent_index in self.skeleton.get_bone_descending_parent_indices(bone, include_self=True):
                track_index = animation.get_track_index_of_bone(parent_index)
                transform = animation_frame[track_index].inverse() @ transform
            return transform
        else:
            raise TypeError("Can only convert Vector3 or TRSTransform.")

    def world_to_local_space_all_frames(
        self, bone: BONE_SPEC_TYPING, point_or_transform: Vector3 | TRSTransform, anim_id: int = None
    ) -> list[Vector3] | list[TRSTransform]:
        """Convert given point or transform (translation and rotation components only) from world space to the local
        space of `bone` by accumulating and applying all parent transforms.

        Returns a full list of new world positions/transforms on every frame.
        """
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise ValueError("Can only do per-frame transformations for interleaved animations.")
        if isinstance(point_or_transform, Vector3):
            point = point_or_transform  # type: Vector3
            world_points = []  # type: list[Vector3]
            for frame in animation.interleaved_data:
                frame_world_point = point.copy()
                for parent_index in self.skeleton.get_bone_descending_parent_indices(bone, include_self=True):
                    track_index = animation.get_track_index_of_bone(parent_index)
                    frame_world_point = frame[track_index].inverse_transform_vector(frame_world_point)
                world_points.append(frame_world_point)
            return world_points
        elif isinstance(point_or_transform, TRSTransform):
            transform = point_or_transform  # type: TRSTransform
            world_transforms = []  # type: list[TRSTransform]
            for frame in animation.interleaved_data:
                frame_world_transform = transform.copy()
                for parent_index in self.skeleton.get_bone_descending_parent_indices(bone, include_self=True):
                    track_index = animation.get_track_index_of_bone(parent_index)
                    frame_world_transform = frame[track_index].inverse() @ frame_world_transform
                world_transforms.append(frame_world_transform)
            return world_transforms
        else:
            raise TypeError("Can only convert Vector3 or TRSTransform.")

    # TODO: "Hand realignment" method.
    """    
    - Let's say that bone R Weapon is a child of R Hand, and we need to realign L Hand to be holding it.
    - Find the point, in R Weapon local space, where we want the left hand to "grasp it".
    - Convert that point to world space in each frame: `grasp_point_world`    
    - Change translation of R Hand such that a passed-in `grasp_point_local` matches `grasp_point_world`.
        - Preserve rotation of R Hand: we are only translating it to correct its position.
        - Just calculate the current world space coordinates for `grasp_point_local` and shift R Hand translation by the
        inverse vector to their difference.
    - Check that this new R Hand translation's world space distance from R UpperArm does not exceed the combined length
    of R UpperArm and R Forearm.
    - Find combination of new R UpperArm ROTATION and R Forearm TRANSLATION that preserves the lengths of R UpperArm and
    R Forearm.
        - This solution will be a "swivel circle" around the vector between R UpperArm (fixed) and R Hand (newly fixed).
    - Select the point on that circle that involves the smallest change in rotation (shortest arc) for R UpperArm. 
    """

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
                    frame.append(bone_qs_transform.to_trs_transform())  # fresh object for each frame
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

    def conform_bone_length_in_animation(self, bone: BONE_SPEC_TYPING, anim_id: int = None, extra_scale=1.0):
        """Scale length of `bone` (translation vector magnitude) in every frame to match its length in the skeleton's
        reference pose. Useful after retargeting, but will generally break IK (such as feet on ground, two-handed
        weapons).

        Use `extra_scale` to apply global scaling to all bone lengths.
        """
        bone = self.skeleton.resolve_bone_spec(bone)
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            # TODO: Should be able to conform spline control points as well.
            raise TypeError("Can only confirm bone length for interleaved animations.")
        reference_pose_transform = self.skeleton.get_bone_reference_pose_transform(bone)
        reference_pose_length = reference_pose_transform.translation.get_magnitude() * extra_scale
        transforms = self.get_bone_interleaved_transforms(bone, anim_id)
        print(f"Conforming bone '{bone.name}' to length {reference_pose_length}.")
        for tf in transforms:
            old_magnitude = abs(tf.translation)
            if old_magnitude != 0:
                tf.translation = tf.translation / old_magnitude * reference_pose_length
            elif reference_pose_length != 0:
                print(f"  Cannot change length 0 bone to length {reference_pose_length}.")

    def conform_all_bone_lengths_in_animation(self, anim_id: int = None, extra_scale=1.0):
        for bone in self.skeleton.bones:
            self.conform_bone_length_in_animation(bone, anim_id, extra_scale)

    def realign_foot_to_ground(
        self, *foot_bones: BONE_SPEC_TYPING, anim_id: int = None, root_bone: BONE_SPEC_TYPING = None, ground_height=0.0
    ):
        """Find the highest shared parent of all `foot_bones` (usually 'Master') and offset its Y translation in every
        frame so that the LOWEST `foot_bone` on that frame has a world-space Y coordinate of `ground_height` (typically
        zero).

        Useful after retargeting and conforming bone lengths, provided that the change in foot bone hierarchies is very
        similar.
        """
        foot_bones = [self.skeleton.resolve_bone_spec(foot_bone) for foot_bone in foot_bones]
        if root_bone is None:
            root_bone = self.skeleton.get_bone_highest_parent(foot_bones[0])
        else:
            root_bone = self.skeleton.resolve_bone_spec(root_bone)
        all_foot_root_tfs = [
            self.get_bone_interleaved_transforms(foot_bone, anim_id, world_space=True)
            for foot_bone in foot_bones
        ]
        true_root_tfs = self.get_bone_interleaved_transforms(root_bone, anim_id)
        for i, true_root_tf in enumerate(true_root_tfs):
            lowest_y = min(frames[i].translation.y for frames in all_foot_root_tfs)
            true_root_tf.translation.y += ground_height - lowest_y

    # TODO: "realign_hand_to_weapon" method that uses minor rotations and stretch (up to some specified max) to place
    #  a hand on a weapon, which can be defined relative to the other hand (to which the weapon is parented).

    def _get_tpose_spline_transform_track(self, bone_index: int) -> SplineTransformTrack:
        bone_qs_transform = self.skeleton.skeleton.referencePose[bone_index]
        return SplineTransformTrack.from_static_transform(
            bone_qs_transform.translation,
            bone_qs_transform.rotation,
            bone_qs_transform.scale,
        )

    def _get_tpose_transform_list(self, bone_index: int, frame_count: int) -> list[TRSTransform]:
        bone_qs_transform = self.skeleton.skeleton.referencePose[bone_index]
        return [bone_qs_transform.to_trs_transform() for _ in range(frame_count)]

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
        self, bone: BONE_SPEC_TYPING, anim_id: int = None, world_space=False,
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

        if not world_space:
            return transforms  # local transforms suffice

        # Compose transforms with all parents.
        frame_count = len(transforms)
        hierarchy = self.skeleton.get_hierarchy_to_bone(bone)
        for parent in reversed(hierarchy[:-1]):  # exclude this bone (already retrieved) and reverse order
            parent_transforms = self.get_bone_interleaved_transforms(parent)
            for i in range(frame_count):
                transforms[i] = parent_transforms[i].compose(transforms[i], scale_translation=True)
        return transforms

    def get_all_world_space_transforms_in_frame(self, frame_index: int, anim_id: int = None) -> list[TRSTransform]:
        """Resolve all transforms to get world space transforms at the given `frame` index.

        TODO: Lots of redundant calculations right now; it would be more efficient to work my way downward rather than
         upward from each bone.
        """
        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        animation.load_interleaved_data()
        if frame_index > len(animation.interleaved_data):
            raise ValueError(f"Frame must be between 0 and {len(animation.interleaved_data)}, not {frame_index}.")
        all_bone_index_hierarchies = self.skeleton.get_all_bone_parent_indices()
        frame_transforms = animation.interleaved_data[frame_index]
        # NOTE: `world_transforms` is ordered by bone, not track. Bones without tracks will have identity transforms.
        world_transforms = [TRSTransform.identity() for _ in self.skeleton.bones]
        mapping = animation.animation_binding.transformTrackToBoneIndices
        for track_index, bone_index in enumerate(mapping):
            bone_index_hierarchy = all_bone_index_hierarchies[bone_index]
            for parent_index in reversed(bone_index_hierarchy):  # start with own local transform and work way upward
                parent_transform = frame_transforms[mapping.index(parent_index)]
                world_transforms[bone_index] = parent_transform @ world_transforms[bone_index]  # scales translation
        return world_transforms

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
                anibnd.find_entry_matching_name(r"[Ss]keleton\.[Hh][Kk][Xx]"), compendium=compendium
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
        if VispyWindow is None:
            raise ModuleNotFoundError("`vispy` package required to plot skeletons.")

        # noinspection PyPackageRequirements
        # Even if only some `bone_names` are given, we collect all of them to draw connective lines from parents.
        bone_translations = [
            scale * self.skeleton.get_bone_reference_pose_transform(bone, world_space=True).translation
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
        if VispyWindow is None:
            raise ModuleNotFoundError("`vispy` package required to plot skeletons.")

        animation = self.get_animation(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only plot interleaved animations.")
        animation.load_interleaved_data()
        world_transforms = self.get_all_world_space_transforms_in_frame(frame, anim_id)

        if window is None:
            window = VispyWindow()

        points = []
        line_points = []
        x_arrow_line_points = []
        x_arrows = []
        z_arrow_line_points = []
        z_arrows = []
        for bone_index, bone_world_transform in enumerate(world_transforms):
            bone = self.skeleton.resolve_bone_spec(bone_index)
            translation = bone_world_transform.translation.to_xzy()
            points.append(translation)
            # if label_bones and (not label_bone_filter or label_bone_filter in bone.name):
            #     ax.text(translation[0], translation[2], translation[1], f"({bone_index}) {bone.name}")

            parent_index = self.skeleton.get_bone_parent_index(bone)
            if parent_index != -1:
                parent_translation = world_transforms[parent_index].translation
                line_points += [parent_translation.to_xzy(), translation]

            # Draw axes along X (red) and Z (green) axes.
            rotation = bone_world_transform.rotation
            x_end = (bone_world_transform.translation + rotation.rotate_vector(Vector3(0.1, 0, 0))).to_xzy()  # X
            z_end = (bone_world_transform.translation + rotation.rotate_vector(Vector3(0, 0, 0.1))).to_xzy()  # Z

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
        """Plot interleaved animation transforms (translation only) in both local bone space and world space."""
        if plt is None or cm is None:
            raise ModuleNotFoundError("`matplotlib` package required to plot.")

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

        for ax, world_space in zip(axes, (False, True)):
            transforms = self.get_bone_interleaved_transforms(bone, anim_id, world_space=world_space)
            if coord in ("x", "y", "z"):
                values = [getattr(t.translation, coord) for t in transforms]
            else:  # magnitude
                values = [abs(t.translation) for t in transforms]
            ax.plot(values, label=bone.name, color=color)
            if legend and not world_space:
                ax.legend()
            if ylim is not None:
                ax.set_ylim(ylim)
        if show:
            plt.show()

    def plot_hierarchy_interleaved_translation(
        self, bone: BONE_SPEC_TYPING, coord: str, anim_id: int = None, title: str = None, ylim=None, show=False
    ):
        """Plot a grid for all bones in the hierarchy up to `bone`, including itself."""
        if plt is None or cm is None:
            raise ModuleNotFoundError("`matplotlib` package required to plot.")
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
