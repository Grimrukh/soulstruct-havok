"""Manager class that combines various HKX files to make animation modification easier.

Currently mainly set up for Havok 2015 (for Nightfall/DSR).
"""
from __future__ import annotations

import abc
import copy
import logging
import typing as tp
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
try:
    import matplotlib.pyplot as plt
    from matplotlib import cm
except ModuleNotFoundError:
    plt = cm = None

from soulstruct.containers import Binder

from soulstruct_havok.spline_compression import *
from soulstruct_havok.tagfile.unpacker import MissingCompendiumError
from soulstruct_havok.utilities.maths import Quaternion, TRSTransform, Vector3

from .file_types import AnimationHKX, SkeletonHKX
from .animation import AnimationContainer
from .skeleton import Skeleton, Bone

try:
    from soulstruct_havok.utilities.vispy_window import VispyWindow  # could be `None` if `vispy` not installed
except ImportError:
    VispyWindow = None

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class BaseANIBND(Binder, abc.ABC):

    ANIMATION_HKX: tp.ClassVar[tp.Type[AnimationHKX]]
    SKELETON_HKX: tp.ClassVar[tp.Type[SkeletonHKX]]
    # TODO: TAE support?

    # Actual HKX files loaded from Binder entries, which will be written again.
    # These should not be directly modified. The `skeleton` property and `__getitem__[anim_id]` method (which returns an
    # `AnimationContainer` wrapper) should be used instead.
    skeleton_hkx: SkeletonHKX | None = None
    animations_hkx: dict[int, AnimationHKX] = field(default_factory=dict)

    # `default_anim_id` will be set to a single animation if only one is loaded. This allows various animation-affecting
    # methods to be used without specifying that lone animation ID every time. It can also be passed in manually.
    default_anim_id: int | None = None
    # Can be passed to `load_from_entries()` to only load certain animations from the Binder.
    animation_ids_to_load: list[int] = field(default_factory=list)

    def load_from_entries(self, *animation_ids_to_load: int):
        """Load managed HKX skeleton and animations from Binder entries.

        Must be called manually so user has a chance to set `animation_ids_to_load` first.
        
        TODO: refactor to `load_animation_entries()`.
        """
        if animation_ids_to_load:
            self.animation_ids_to_load = list(animation_ids_to_load)
        if not self.entries:
            # No Binder entries to process. Just check default animation ID assignment.
            if self.default_anim_id is None and len(self.animations_hkx) == 1:
                self.default_anim_id = list(self.animations_hkx)[0]
            return

        compendium, compendium_name = self.ANIMATION_HKX.get_compendium_from_binder(self)
        try:
            skeleton_entry = self.find_entry_matching_name(r"[Ss]keleton\.[Hh][Kk][Xx]")
            self.skeleton_hkx = self.SKELETON_HKX.from_bytes(skeleton_entry, compendium=compendium)

            if not self.animation_ids_to_load:
                # Load ALL animations.
                self.animations_hkx = {}
                for anim_entry in self.find_entries_matching_name(r"a[\d_]+\.[Hh][Kk][Xx]"):
                    anim_id = int(anim_entry.minimal_stem[1:])
                    self.animations_hkx[anim_id] = self.ANIMATION_HKX.from_bytes(anim_entry, compendium=compendium)
            else:
                # Load selected (also asserted) animation IDs only.
                self.animations_hkx = {}
                for anim_id in self.animation_ids_to_load:
                    entry_name = self.animation_id_to_entry_basename(anim_id)
                    try:
                        anim_entry = self.find_entry_name(entry_name)
                    except KeyError:
                        raise ValueError(f"Could not find animation entry '{entry_name}' for animation ID {anim_id}.")
                    self.animations_hkx[anim_id] = self.ANIMATION_HKX.from_bytes(anim_entry, compendium=compendium)

        except MissingCompendiumError:
            if compendium_name != "":
                raise MissingCompendiumError(
                    f"One or more Binder HKX entries require a compendium, but compendium '{compendium_name}' "
                    f"could not be found in the Binder. Use `compendium_name` argument if it has another name."
                )
            raise MissingCompendiumError(
                f"One or more Binder HKX entries require a compendium, but `compendium_name` was not given and a "
                f"'.compendium' entry could not be found in the Binder."
            )

        # Only set default if a single animation was loaded from the ANIBND.
        self.default_anim_id = list(self.animations_hkx)[0] if len(self.animations_hkx) == 1 else None

    @property
    def skeleton(self) -> Skeleton:
        return self.skeleton_hkx.skeleton

    @property
    def bones(self) -> list[Bone]:
        return self.skeleton.bones

    @property
    def bones_by_name(self) -> dict[str, Bone]:
        return self.skeleton.bones_by_name

    def get_animation_container(self, anim_id: int = None) -> AnimationContainer:
        if anim_id is None:
            if self.default_anim_id is None:
                raise ValueError("Default animation ID has not been set.")
            anim_id = self.default_anim_id
        return self.animations_hkx[anim_id].animation_container

    def __getitem__(self, anim_id: int) -> AnimationContainer:
        return self.get_animation_container(anim_id)

    def copy_animation(self, anim_id: int, new_anim_id: int, overwrite=False):
        """Make a deep copy of an `AnimationHKX` file instance (corresponding to a new or overwritten Binder entry)."""
        if new_anim_id in self.animations_hkx and not overwrite:
            raise ValueError(f"Animation ID {new_anim_id} already exists, and `overwrite=False`.")
        self.animations_hkx[new_anim_id] = self.animations_hkx[anim_id].copy()

    def rotate_bone_track(
        self,
        bone: Bone,
        rotation: Quaternion | list[Quaternion],
        anim_id: int = None,
        compensate_children=False,
    ):
        """Apply `rotation` to `bone.rotation` in every animation frame. Requires interleaved animation.

        If `compensate_children=True` (NOT default), children of `bone` will be transformed in a way that preserves
        their transforms in world space.
        """
        animation = self.get_animation_container(anim_id)
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
        parent_bone: Bone,
        swiveling_bone: Bone,
        child_bone: Bone,
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
        if swiveling_bone.parent is not parent_bone:
            raise ValueError("Swiveling bone must be an immediate child of parent bone.")
        if child_bone.parent is not swiveling_bone:
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
        bone: Bone,
        transform: TRSTransform | list[TRSTransform],
        anim_id: int = None,
        rotate_parent=True,
        compensate_children=False,
        rotation_orbits_child: Bone = None,
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
        animation = self.get_animation_container(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only use `proper_transform_bone_track()` for interleaved animations.")
        bone_tfs = self.get_bone_interleaved_transforms(bone, anim_id)

        if isinstance(transform, (list, tuple)) and len(transform) != len(bone_tfs):
            raise ValueError(f"Received a list of {len(transform)} transforms, but there are {len(bone_tfs)} frames.")

        if bone.parent is None and (rotate_parent or compensate_children):
            raise ValueError(
                f"Bone '{bone.name}' has no parent. You must set `rotate_parent=False` and `compensate_children=False`."
            )
        parent_tfs = self.get_bone_interleaved_transforms(bone.parent, anim_id)

        print(f"Transforming bone {bone.name} with reference to parent {bone.parent.name}.")

        target_bone = None
        target_bone_tfs = []
        initial_root_target_tfs = []
        if rotation_orbits_child:
            if rotation_orbits_child.parent is not bone:
                raise ValueError(
                    f"Bone '{rotation_orbits_child.name}' (`rotation_orbits_child` target) is not a child of "
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
        source_anibnd: BaseANIBND,
        source_anim_id: int,
        dest_anim_id: int,
        bone_name_mapping: dict[str, str | None | list[str]],
    ):
        """Read `source_anim_id` from `source_anibnd` and use `bone_name_mapping` to convert the animation tracks to
        `new_anim_id` in this manager.

        `bone_name_mapping` should map the names of bones in THIS skeleton to those in the `source_anibnd` skeleton, or
        `None` if that bone should be ignored (has no corresponding source), or a list of bone names if it should
        inherit the accumulated transforms of multiple (parent-child) bones.
        """
        source_animation = source_anibnd.get_animation_container(source_anim_id)
        dest_animation = self.get_animation_container(dest_anim_id)
        source_animation.load_interleaved_data()
        dest_animation.load_interleaved_data()

        frame_count = source_animation.frame_count
        new_frames = [[] for _ in range(frame_count)]  # type: list[list[TRSTransform]]
        for i, bone in enumerate(self.bones):
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
                    component_transforms = source_anibnd.get_bone_interleaved_transforms(
                        source_anibnd.bones_by_name[component_bone_name], source_anim_id
                    )
                    for frame, component_t in zip(new_frames, component_transforms):
                        if invert:
                            frame[-1] = component_t.inverse().compose(frame[-1], scale_translation=True)
                        else:
                            frame[-1] = component_t.compose(frame[-1], scale_translation=True)

                # _LOGGER.info(f"Bone '{bone.name}' mapped to composed source bones: {source_bone}")
            elif isinstance(source_bone, str):
                # _LOGGER.info(f"Bone '{bone.name}' mapped to source bone '{source_bone}'.")
                bone_transforms = source_anibnd.get_bone_interleaved_transforms(
                    source_anibnd.bones_by_name[source_bone], source_anim_id
                )
                for frame, bone_t in zip(new_frames, bone_transforms):
                    frame.append(copy.deepcopy(bone_t))  # new object
            else:
                raise TypeError(
                    f"Invalid source bone: {source_bone}. Should be None, a bone name, or a list of bone names."
                )

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
        source_anibnd: BaseANIBND,
        source_anim_id: int,
        dest_anim_id: int,
        bone_name_mapping: dict[str, str | None | list[str]],
    ):
        """Read `source_anim_id` from `source_anibnd` and use `bone_name_mapping` to convert the animation tracks to
        `new_anim_id` in this manager.

        `bone_name_mapping` should map the names of bones in THIS skeleton to those in `source_anibnd`'s skeleton.
        """
        source_animation = source_anibnd.get_animation_container(source_anim_id)
        dest_animation = self.get_animation_container(dest_anim_id)
        source_animation.load_spline_data()
        dest_animation.load_spline_data()

        new_block = []  # type: list[SplineTransformTrack]
        for i, bone in enumerate(self.bones):
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
            elif isinstance(source_bone_name, str):
                # _LOGGER.info(f"Bone '{bone.name}' mapped to source bone '{source_bone_name}'.")
                source_track = source_anibnd.get_bone_spline_animation_track(
                    self.bones_by_name[source_bone_name], source_anim_id
                )
                new_block.append(copy.deepcopy(source_track))
            else:
                raise TypeError(f"Invalid source bone: {source_bone_name}. Should be None, a name, or list of names.")

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

    def conform_bone_length_in_animation(self, bone: Bone, anim_id: int = None, extra_scale=1.0):
        """Scale length of `bone` (translation vector magnitude) in every frame to match its length in the skeleton's
        reference pose. Useful after retargeting, but will generally break IK (such as feet on ground, two-handed
        weapons).

        Use `extra_scale` to apply global scaling to all bone lengths.
        """
        animation = self.get_animation_container(anim_id)
        if not animation.is_interleaved:
            # TODO: Should be able to conform spline control points as well.
            raise TypeError("Can only confirm bone length for interleaved animations.")
        reference_pose_transform = bone.get_reference_pose()
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
        for bone in self.bones:
            self.conform_bone_length_in_animation(bone, anim_id, extra_scale)

    def realign_foot_to_ground(
        self, *foot_bones: Bone, anim_id: int = None, root_bone: Bone = None, ground_height=0.0
    ):
        """Find the highest shared parent of all `foot_bones` (usually 'Master') and offset its Y translation in every
        frame so that the LOWEST `foot_bone` on that frame has a world-space Y coordinate of `ground_height` (typically
        zero).

        Useful after retargeting and conforming bone lengths, provided that the change in foot bone hierarchies is very
        similar.
        """
        if root_bone is None:
            root_bone = foot_bones[0].get_root_parent()
        all_foot_root_tfs = [
            self.get_bone_interleaved_transforms(foot_bone, anim_id, in_armature_space=True)
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

    def get_bone_spline_animation_track(self, bone: Bone, anim_id: int = None) -> SplineTransformTrack:
        animation = self.get_animation_container(anim_id)
        if not animation.is_spline:
            raise TypeError("Can only get bone animation tracks for spline-compressed animation.")
        animation.load_spline_data()
        mapping = animation.animation_binding.transformTrackToBoneIndices
        track_index = mapping.index(bone.index)
        return animation.spline_data.blocks[0][track_index]

    def get_immediate_child_bone_spline_animation_tracks(
        self, parent_bone: Bone, anim_id: int = None
    ) -> list[tuple[int, SplineTransformTrack]]:
        """Get a list of `(int, track)` tuples for all immediate child bones of `parent_bone_name_or_index`."""
        animation = self.get_animation_container(anim_id)
        if not animation.is_spline:
            raise TypeError("Can only get bone animation tracks for spline-compressed animation.")
        animation.load_spline_data()
        mapping = animation.animation_binding.transformTrackToBoneIndices
        child_track_indices = [mapping.index(child_bone.index) for child_bone in parent_bone.children]
        block = animation.spline_data.blocks[0]
        return [(i, block[i]) for i in child_track_indices]

    def get_bone_interleaved_transforms(
        self, bone: Bone, anim_id: int = None, in_armature_space=False,
    ) -> list[TRSTransform]:
        """Get all frame transforms (optionally in armature space) for given bone."""
        animation = self.get_animation_container(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        animation.load_interleaved_data()
        mapping = animation.animation_binding.transformTrackToBoneIndices
        track_index = mapping.index(bone.index)
        transforms = [frame[track_index] for frame in animation.interleaved_data]

        if not in_armature_space:
            return transforms  # local transforms requested

        # Compose transforms with all parents.
        frame_count = len(transforms)
        for parent in bone.ascending_hierarchy[1:]:  # exclude this bone (already retrieved)
            parent_transforms = self.get_bone_interleaved_transforms(parent)
            for i in range(frame_count):
                transforms[i] = parent_transforms[i] @ transforms[i]
        return transforms

    def get_all_armature_space_transforms_in_frame(self, frame_index: int, anim_id: int = None) -> list[TRSTransform]:
        """Resolve all transforms to get all bones' armature space transforms at the given `frame_index`.

        Avoids recomputing transforms multiple times; each bone is only processed once, using parents' accumulating
        world transforms.
        """
        animation = self.get_animation_container(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        animation.load_interleaved_data()
        if frame_index > len(animation.interleaved_data):
            raise ValueError(f"Frame must be between 0 and {len(animation.interleaved_data)}, not {frame_index}.")

        frame_local_transforms = animation.interleaved_data[frame_index]
        # NOTE: `world_transforms` is ordered by bone, not track. Bones without tracks will have identity transforms.
        track_world_transforms = [TRSTransform.identity() for _ in self.bones]
        track_bone_indices = animation.animation_binding.transformTrackToBoneIndices

        def bone_local_to_world(bone: Bone, world_transform: TRSTransform):
            track_index = track_bone_indices.index(bone.index)
            track_world_transforms[track_index] = world_transform @ frame_local_transforms[track_index]
            # Recur on children, using this bone's just-computed world transform.
            for child_bone in bone.children:
                bone_local_to_world(child_bone, track_world_transforms[track_index])

        for root_bone in self.skeleton.get_root_bones():
            # Start recurring transformer on root bones. (Their local space IS armature space.)
            bone_local_to_world(root_bone, TRSTransform.identity())

        return track_world_transforms

    def get_immediate_child_bone_interleaved_animation_transforms(
        self, parent_bone: Bone, anim_id: int = None
    ) -> list[tuple[Bone, list[TRSTransform]]]:
        """Get a list of `(int, track)` tuples for all immediate child bones of `parent_bone_name_or_index`."""
        animation = self.get_animation_container(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only get bone animation tracks for interleaved animation.")
        animation.load_interleaved_data()
        mapping = animation.animation_binding.transformTrackToBoneIndices
        child_bones_and_transforms = []
        for child_bone in parent_bone.children:
            child_track_index = mapping.index(child_bone.index)
            child_bones_and_transforms.append(
                (
                    child_bone,
                    [frame[child_track_index] for frame in animation.interleaved_data],
                ),
            )
        return child_bones_and_transforms

    # region Read/Write Methods

    def write_anim_ids_into_anibnd(
        self, anibnd_path: Path | str, *anim_ids: int, from_bak=False, write_path: Path | str = None
    ):
        """Open an existing `.anibnd` Binder, write given `anim_ids` into it, and write it back to disk at `write_path`
        (or back to `anibnd_path` by default)."""
        anibnd = Binder.from_bak(anibnd_path) if from_bak else Binder.from_path(anibnd_path)
        for anim_id in anim_ids:
            animation_hkx = self.animations_hkx[anim_id]
            anibnd[self.animation_id_to_entry_basename(anim_id)].set_from_binary_file(animation_hkx)
        if write_path is None:
            write_path = anibnd_path
        anibnd.write(file_path=write_path)
        if write_path != anibnd_path:
            _LOGGER.info(f"Animations {', '.join(str(x) for x in anim_ids)} written to {anibnd_path} at {write_path}.")
        else:
            _LOGGER.info(f"Animations {', '.join(str(x) for x in anim_ids)} written into {anibnd_path}.")

    def write_all_into_anibnd(self, anibnd_path: Path | str, from_bak=False, write_path: Path | str = None):
        """Open an existing `.anibnd` Binder, write the opened skeleton and ALL opened animations into it, and write it
        back to disk at `write_path` (or back to `anibnd_path` by default)."""
        anibnd = Binder.from_bak(anibnd_path) if from_bak else Binder.from_path(anibnd_path)
        anibnd.find_entry_matching_name(r"[Ss]keleton\.[HKX|hkx]").set_from_binary_file(self.skeleton_hkx)
        for anim_id, animation_hkx in self.animations_hkx.items():
            anibnd[self.animation_id_to_entry_basename(anim_id)].set_from_binary_file(animation_hkx)
        anibnd.write(file_path=write_path)  # will default to same path
        _LOGGER.info(f"Skeleton and all animations written into {anibnd_path}.")
    # endregion

    # region Plotting Methods

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
            scale * bone.get_reference_pose_in_arma_space().translation
            for bone in self.bones
        ]

        if not bone_names:
            bone_names = [bone.name for bone in self.bones]

        if window is None:
            window = VispyWindow()

        points = []
        lines = []
        for bone_name in bone_names:
            bone = self.bones_by_name[bone_name]
            translation = bone_translations[bone.index]
            points.append(translation.to_xzy())

            if bone.parent is not None:
                parent_translation = bone_translations[bone.parent.index]
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

        animation = self.get_animation_container(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only plot interleaved animations.")
        animation.load_interleaved_data()
        world_transforms = self.get_all_armature_space_transforms_in_frame(frame, anim_id)

        if window is None:
            window = VispyWindow()

        points = []
        line_points = []
        x_arrow_line_points = []
        x_arrows = []
        z_arrow_line_points = []
        z_arrows = []
        for bone_index, bone_world_transform in enumerate(world_transforms):
            bone = self.bones[bone_index]
            translation = bone_world_transform.translation.to_xzy()
            points.append(translation)
            # if label_bones and (not label_bone_filter or label_bone_filter in bone.name):
            #     ax.text(translation[0], translation[2], translation[1], f"({bone_index}) {bone.name}")

            if bone.parent is not None:
                parent_translation = world_transforms[bone.parent.index].translation
                line_points += [parent_translation.to_xzy(), translation]

            # Draw axes along X (red) and Z (green) axes.
            rotation = bone_world_transform.rotation
            x_end = (bone_world_transform.translation + rotation.rotate_vector(Vector3((0.1, 0, 0)))).to_xzy()  # X
            z_end = (bone_world_transform.translation + rotation.rotate_vector(Vector3((0, 0, 0.1)))).to_xzy()  # Z

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
        bone: Bone,
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
        animation = self.get_animation_container(anim_id)
        if not animation.is_interleaved:
            raise TypeError("Can only plot interleaved animations.")
        animation.load_interleaved_data()
        if title is None:
            title = bone.name
        if axes is None:
            fig, axes = plt.subplots(ncols=2, figsize=(10, 5))
            if title:
                fig.suptitle(title)

        for ax, in_armature_space in zip(axes, (False, True)):
            transforms = self.get_bone_interleaved_transforms(bone, anim_id, in_armature_space=in_armature_space)
            if coord in ("x", "y", "z"):
                values = [getattr(t.translation, coord) for t in transforms]
            else:  # magnitude
                values = [abs(t.translation) for t in transforms]
            ax.plot(values, label=bone.name, color=color)
            if legend and not in_armature_space:
                ax.legend()
            if ylim is not None:
                ax.set_ylim(ylim)
        if show:
            plt.show()

    def plot_hierarchy_interleaved_translation(
        self, bone: Bone, coord: str, anim_id: int = None, title: str = None, ylim=None, show=False
    ):
        """Plot a grid for all bones in the hierarchy up to `bone`, including itself."""
        if plt is None or cm is None:
            raise ModuleNotFoundError("`matplotlib` package required to plot.")
        fig, axes = plt.subplots(ncols=2, figsize=(10, 5))
        if title is None:
            title = f"{bone.name} Hierarchy"
        fig.suptitle(title)
        fig.tight_layout()
        inferno = cm.get_cmap("inferno")
        for i, parent_bone in enumerate(bone.descending_hierarchy):
            color = inferno(i / len(bone.descending_hierarchy))
            color = (color[0], color[1], color[2], color[3] * 0.8)
            self.plot_interleaved_translation(
                parent_bone, coord, anim_id, color=color, show=False, axes=axes, ylim=ylim, legend=False
            )
        axes[0].legend()
        if show:
            plt.show()

    # endregion

    @staticmethod
    @abc.abstractmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        ...
