from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX"]

from soulstruct_havok.types import hk2010
from soulstruct_havok.wrappers.base import (
    BaseAnimationHKX as BaseAnimationHKX,
    BaseSkeletonHKX as BaseSkeletonHKX,
    BaseClothHKX as BaseClothHKX,
    BaseRagdollHKX as BaseRagdollHKX,
)


class HKXMixin2010:
    root: hk2010.hkRootLevelContainer
    TYPES_MODULE = hk2010


class AnimationHKX(HKXMixin2010, BaseAnimationHKX):
    pass


class SkeletonHKX(HKXMixin2010, BaseSkeletonHKX):
    pass


class ClothHKX(HKXMixin2010, BaseClothHKX):
    pass


class RagdollHKX(HKXMixin2010, BaseRagdollHKX):
    pass
