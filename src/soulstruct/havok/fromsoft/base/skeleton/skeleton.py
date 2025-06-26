from __future__ import annotations

__all__ = ["Skeleton"]

import abc
import logging
import typing as tp
from dataclasses import dataclass, field

from soulstruct.havok.enums import HavokModule
from soulstruct.havok.utilities.maths import Vector3, Vector4, TRSTransform

from ..type_vars import SKELETON_T, BONE_T
from .bone import Bone

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, repr=False)
class Skeleton(tp.Generic[SKELETON_T, BONE_T], abc.ABC):
    """Loads HKX objects that are found in a "Skeleton" HKX file (inside `anibnd` binder, usually `Skeleton.HKX`)."""

    havok_module: HavokModule
    skeleton: SKELETON_T

    bones: list[Bone] = field(init=False)
    bones_by_name: None | dict[str, Bone] = field(init=False)  # only available if all names are unique

    def __post_init__(self):
        self.refresh_bones()

    def refresh_bones(self):
        """Rebuilds the `bones` list and `bones_by_name` dict from the `skeleton` object, using `Bone` wrappers rather
        than the raw `hkaBone` types (so inter-bone references can be better used)."""

        bones_by_index = {}  # type: dict[int, Bone]  # created depth-first and sorted at end
        all_child_indices = {}
        all_descending_hierarchy_indices = {}

        found_names = set()
        repeated_names = []

        def _create_bone_wrapper(hka_bone: BONE_T, parent: None | Bone, parent_indices: list[int]):
            index = self.skeleton.bones.index(hka_bone)
            descending_indices = all_descending_hierarchy_indices[index] = parent_indices + [index]
            child_indices = [i for i, parent_index in enumerate(self.skeleton.parentIndices) if parent_index == index]
            all_child_indices[index] = child_indices
            bone_wrapper = Bone(
                _skeleton=self.skeleton,
                index=index,
                name=hka_bone.name,
                parent=parent,  # reference definitely already created
                # Other reference tuples assigned below.
            )
            bones_by_index[index] = bone_wrapper
            if hka_bone.name in found_names:
                repeated_names.append(hka_bone.name)
            else:
                found_names.add(hka_bone.name)

            for child_index in child_indices:
                _create_bone_wrapper(self.skeleton.bones[child_index], bone_wrapper, descending_indices)

        root_hka_bones = [b for i, b in enumerate(self.skeleton.bones) if self.skeleton.parentIndices[i] == -1]

        for root_hka_bone in root_hka_bones:
            _create_bone_wrapper(root_hka_bone, None, [])

        self.bones = [bones_by_index[i] for i in sorted(bones_by_index)]

        # Assign bone references (bypassing `frozen=True`).
        for bone in self.bones:
            children = tuple(self.bones[i] for i in all_child_indices[bone.index])
            descending_hierarchy = tuple(self.bones[i] for i in all_descending_hierarchy_indices[bone.index])
            # TODO: why object.__setattr__?
            object.__setattr__(bone, "children", children)
            object.__setattr__(bone, "descending_hierarchy", descending_hierarchy)
            object.__setattr__(bone, "ascending_hierarchy", tuple(reversed(descending_hierarchy)))

        if repeated_names:
            _LOGGER.warning(
                f"Repeated bone names in this skeleton: {repeated_names}. `SkeletonHKX.bones_by_name` not available. "
                f"Bones must be accessed by index from `SkeletonHKX.bones`.")
            self.bones_by_name = None
        else:
            self.bones_by_name = {bone.name: bone for bone in self.bones}  # ordered by skeleton index

    def get_root_bones(self) -> list[Bone]:
        """Get all root (i.e. parent-less) bones."""
        return [bone for bone in self.bones if bone.parent is None]

    def get_root_bone_indices(self) -> list[int]:
        """Get all root (i.e. parent-less) bone indices."""
        return [i for i, bone in enumerate(self.bones) if bone.parent is None]

    def get_reference_poses(self) -> dict[str, TRSTransform]:
        """Get a dictionary mapping bone names to their reference poses."""
        return {bone.name: bone.get_reference_pose() for bone in self.bones}

    def get_arma_space_reference_poses(self) -> dict[str, TRSTransform]:
        """Get a dictionary mapping bone names to their reference poses in armature space."""

        # We start with local reference poses, and compose parent poses from the top (root bones) down.
        bone_arma_poses = self.get_reference_poses()

        def local_to_parent(bone_: Bone, parent_ref_pose: TRSTransform):
            bone_arma_poses[bone_.name] = parent_ref_pose @ bone_arma_poses[bone_.name]
            # Recur on children, using this bone's just-computed armature-space reference pose.
            for child_bone in bone_.children:
                local_to_parent(child_bone, bone_arma_poses[bone_.name])

        for root_bone in self.get_root_bones():
            # Start recurring transformer on root bones. (Their local space IS armature space.)
            local_to_parent(root_bone, TRSTransform.identity())

        return bone_arma_poses

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        """Scale all bone translations in place by `scale_factor`."""
        if isinstance(scale_factor, Vector3):
            scale_factor = Vector4.from_vector3(scale_factor)
        for pose in self.skeleton.referencePose:
            pose.translation *= scale_factor

    def delete_bone_index(self, bone_index) -> int:
        """Delete a bone and all of its children. Returns the number of bones deleted."""
        children = self.bones[bone_index].get_all_children()
        delete_indices = [bone_index] + [child.index for child in children]
        self.skeleton.bones = [hka_bone for i, hka_bone in enumerate(self.skeleton.bones) if i not in delete_indices]
        self.refresh_bones()
        return len(delete_indices)

    def print_bone_tree(self, bone_index: int = None, indent=""):
        """Print indented (depth-first) tree of bone names."""

        def _print_bone_tree(bone: Bone, _indent: str):
            print(_indent + bone.name)
            for child in bone.children:
                _print_bone_tree(child, _indent + "    ")

        top_bone = self.bones[0] if bone_index is None else self.bones[bone_index]
        _print_bone_tree(top_bone, _indent=indent)

    # TODO: repr
