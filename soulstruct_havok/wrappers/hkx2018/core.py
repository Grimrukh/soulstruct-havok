from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX"]

from soulstruct_havok.types import hk2018
from soulstruct_havok.wrappers.base import (
    BaseAnimationHKX as BaseAnimationHKX,
    BaseSkeletonHKX as BaseSkeletonHKX,
    BaseClothHKX as BaseClothHKX,
    BaseRagdollHKX as BaseRagdollHKX,
)


class HKXMixin2018:
    root: hk2018.hkRootLevelContainer
    TYPES_MODULE = hk2018


class AnimationHKX(HKXMixin2018, BaseAnimationHKX):
    pass


class SkeletonHKX(HKXMixin2018, BaseSkeletonHKX):
    pass


class ClothHKX(HKXMixin2018, BaseClothHKX):
    pass


class RagdollHKX(HKXMixin2018, BaseRagdollHKX):
    pass
