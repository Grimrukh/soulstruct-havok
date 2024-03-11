from __future__ import annotations

__all__ = ["Bone"]

import logging
import typing as tp
from dataclasses import dataclass

from soulstruct_havok.utilities.maths import TRSTransform

from ..type_vars import SKELETON_T

_LOGGER = logging.getLogger("soulstruct_havok")


@dataclass(slots=True, frozen=True, repr=False)
class Bone(tp.Generic[SKELETON_T]):
    """Wraps the various `hkaBone` Havok classes to add explicit parent references, index information, and so on."""
    _skeleton: SKELETON_T
    index: int
    name: str
    parent: None | Bone
    children: tuple[Bone] = ()
    descending_hierarchy: tuple[Bone] = ()  # descending, from root to self (inclusive)
    ascending_hierarchy: tuple[Bone] = ()  # ascending, from self to root (inclusive)

    # Reference poses are likely enough to change that we don't cache them.

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

    def __repr__(self) -> str:
        parent = self.parent.name if self.parent else None
        return f"{self.__class__.__name__}(index={self.index}, name={self.name!r}, parent={parent!r})"
