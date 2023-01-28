from __future__ import annotations

import abc
import logging
import typing as tp
from dataclasses import dataclass

from soulstruct_havok.utilities.maths import TRSTransform
from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2018

from .core import BaseWrapperHKX

_LOGGER = logging.getLogger(__name__)


SKELETON_TYPING = tp.Union[
    hk2010.hkaSkeleton, hk2014.hkaSkeleton, hk2015.hkaSkeleton, hk2018.hkaSkeleton,
]
BONE_TYPING = tp.Union[
    hk2010.hkaBone, hk2014.hkaBone, hk2015.hkaBone, hk2018.hkaBone,
]


@dataclass(slots=True, frozen=True)
class BoneWrapper:
    """Wraps the various `hkaBone` Havok classes to add explicit parent references, index information, and so on."""
    _skeleton: SKELETON_TYPING
    index: int
    name: str
    parent: None | BoneWrapper
    children: tuple[BoneWrapper] = ()
    descending_hierarchy: tuple[BoneWrapper] = ()  # descending, inclusive
    ascending_hierarchy: tuple[BoneWrapper] = ()  # ascending, inclusive

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

    def get_root_parent(self) -> BoneWrapper:
        bone = self
        while bone.parent is not None:
            bone = bone.parent
        return bone

    def get_all_children(self) -> list[BoneWrapper]:
        """Recursively get all children of this bone, in depth-first order."""

        children = []

        def get_children(bone: BoneWrapper):
            for child in bone.children:
                if child in children:
                    raise RecursionError(f"Bone {child.name} appears to have multiple parents.")
                children.append(child)
                get_children(child)

        get_children(self)

        return children


class BaseSkeletonHKX(BaseWrapperHKX, abc.ABC):
    """Loads HKX objects that are found in a "Skeleton" HKX file (inside `anibnd` binder, usually `Skeleton.HKX`)."""

    skeleton: SKELETON_TYPING

    bones: list[BoneWrapper]
    bones_by_name: None | dict[str, BoneWrapper]  # only available if all names are unique

    def create_attributes(self):
        animation_container = self.get_variant_index(0, "hkaAnimationContainer")
        self.skeleton = animation_container.skeletons[0]
        self.regenerate_bone_wrappers()

    def regenerate_bone_wrappers(self):

        bones_by_index = {}  # type: dict[int, BoneWrapper]
        all_child_indices = {}
        all_descending_hierarchy_indices = {}

        found_names = set()
        repeated_names = []

        def _create_bone_wrapper(hka_bone: BONE_TYPING, parent: None | BoneWrapper, parent_indices: list[int]):
            index = self.skeleton.bones.index(hka_bone)
            descending_indices = all_descending_hierarchy_indices[index] = parent_indices + [index]
            child_indices = [i for i, parent_index in enumerate(self.skeleton.parentIndices) if parent_index == index]
            all_child_indices[index] = child_indices
            bone_wrapper = BoneWrapper(
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

    def get_root_bones(self) -> list[BoneWrapper]:
        """Get all root (i.e. parent-less) bones."""
        return [bone for bone in self.bones if bone.parent is None]

    def get_root_bone_indices(self) -> list[int]:
        """Get all root (i.e. parent-less) bone indices."""
        return [i for i, bone in enumerate(self.bones) if bone.parent is None]

    def scale(self, factor: float):
        """Scale all bone translations in place by `factor`."""
        # TODO: rename `scale_all_bone_translations`
        for pose in self.skeleton.referencePose:
            pose.translation = tuple(x * factor for x in pose.translation)

    def delete_bone_index(self, bone_index) -> int:
        """Delete a bone and all of its children. Returns the number of bones deleted."""
        children = self.bones[bone_index].get_all_children()
        delete_indices = [bone_index] + [child.index for child in children]
        self.skeleton.bones = [hka_bone for i, hka_bone in enumerate(self.skeleton.bones) if i not in delete_indices]
        self.regenerate_bone_wrappers()
        return len(delete_indices)

    def print_bone_tree(self, bone_index: int = None, indent=""):
        """Print indented (depth-first) tree of bone names."""

        def _print_bone_tree(bone: BoneWrapper, _indent: str):
            print(indent + bone.name)
            for child in bone.children:
                _print_bone_tree(child, _indent + "    ")

        top_bone = self.bones[0] if bone_index is None else self.bones[bone_index]
        _print_bone_tree(top_bone, _indent=indent)
