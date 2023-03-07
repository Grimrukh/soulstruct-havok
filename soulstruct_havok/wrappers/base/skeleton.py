from __future__ import annotations

__all__ = ["Bone", "Skeleton", "SkeletonMapper"]

import abc
import logging
import typing as tp
from dataclasses import dataclass
from types import ModuleType

from soulstruct_havok.utilities.maths import TRSTransform, Vector3, Vector4

from .type_vars import SKELETON_T, SKELETON_MAPPER_T, BONE_T

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class Bone(tp.Generic[SKELETON_T]):
    """Wraps the various `hkaBone` Havok classes to add explicit parent references, index information, and so on."""
    _skeleton: SKELETON_T
    index: int
    name: str
    parent: None | Bone
    children: tuple[Bone] = ()
    descending_hierarchy: tuple[Bone] = ()  # descending, inclusive
    ascending_hierarchy: tuple[Bone] = ()  # ascending, inclusive

    # Reference poses are likely enough to change that we don't cache them:

    def get_reference_pose(self) -> TRSTransform:
        return self._skeleton.referencePose[self.index].to_trs_transform()

    def get_reference_pose_in_arma_space(self) -> TRSTransform:
        """NOTE: If you need ALL bones in armature space, it is better to use:
            `SkeletonHKX.get_all_reference_poses_in_arma_space()`
        to avoid excessive, redundant `TRSTransform` creation and multiplication.
        """
        transform = TRSTransform.identity()
        for bone in self.ascending_hierarchy:
            transform = bone.get_reference_pose() @ transform
        return transform

    def get_root_parent(self) -> Bone:
        bone = self
        while bone.parent is not None:
            bone = bone.parent
        return bone

    def get_all_children(self) -> list[Bone]:
        """Recursively get all children of this bone, in depth-first order."""

        children = []

        def get_children(bone: Bone):
            for child in bone.children:
                if child in children:
                    raise RecursionError(f"Bone {child.name} appears to have multiple parents.")
                children.append(child)
                get_children(child)

        get_children(self)

        return children


class Skeleton(tp.Generic[SKELETON_T, BONE_T], abc.ABC):
    """Loads HKX objects that are found in a "Skeleton" HKX file (inside `anibnd` binder, usually `Skeleton.HKX`)."""

    types_module: ModuleType
    skeleton: SKELETON_T

    bones: list[Bone]
    bones_by_name: None | dict[str, Bone]  # only available if all names are unique

    def __init__(self, types_module: ModuleType, skeleton: SKELETON_T):
        self.types_module = types_module
        self.skeleton = skeleton
        self.regenerate_bone_wrappers()

    def regenerate_bone_wrappers(self):
        """Rebuilds the `bones` list and `bones_by_name` dict from the `skeleton` object, using `Bone` wrappers rather
        than the raw `hkaBone` types (so inter-bone references can be better used)."""

        bones_by_index = {}  # type: dict[int, Bone]
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

        self.bones = list(bones_by_index.values())

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
        self.regenerate_bone_wrappers()
        return len(delete_indices)

    def print_bone_tree(self, bone_index: int = None, indent=""):
        """Print indented (depth-first) tree of bone names."""

        def _print_bone_tree(bone: Bone, _indent: str):
            print(indent + bone.name)
            for child in bone.children:
                _print_bone_tree(child, _indent + "    ")

        top_bone = self.bones[0] if bone_index is None else self.bones[bone_index]
        _print_bone_tree(top_bone, _indent=indent)


class SkeletonMapper(tp.Generic[SKELETON_MAPPER_T]):

    types_module: ModuleType
    skeleton_mapper: SKELETON_MAPPER_T

    def __init__(self, types_module: ModuleType, skeleton_mapper: SKELETON_MAPPER_T):
        self.types_module = types_module
        self.skeleton_mapper = skeleton_mapper

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        if isinstance(scale_factor, Vector3):
            scale_factor = Vector4.from_vector3(scale_factor)
        for simple in self.skeleton_mapper.mapping.simpleMappings:
            simple.aFromBTransform.translation *= scale_factor
        for chain in self.skeleton_mapper.mapping.chainMappings:
            chain.startAFromBTransform.translation *= scale_factor
