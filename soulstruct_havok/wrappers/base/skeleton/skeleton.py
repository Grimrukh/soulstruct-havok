from __future__ import annotations

__all__ = ["Skeleton"]

import abc
import logging
import typing as tp
from dataclasses import dataclass, field
from types import ModuleType

from soulstruct_havok.utilities.maths import Vector3, Vector4

from ..type_vars import SKELETON_T, BONE_T
from .bone import Bone

_LOGGER = logging.getLogger("soulstruct_havok")


@dataclass(slots=True, repr=False)
class Skeleton(tp.Generic[SKELETON_T, BONE_T], abc.ABC):
    """Loads HKX objects that are found in a "Skeleton" HKX file (inside `anibnd` binder, usually `Skeleton.HKX`)."""

    types_module: ModuleType
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
