from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX"]

from soulstruct_havok.types import hk2014
from soulstruct_havok.types.hk2014 import *
from soulstruct_havok.wrappers.base import *
from soulstruct_havok.wrappers.base.file_types import (
    AnimationHKX as BaseAnimationHKX,
    SkeletonHKX as BaseSkeletonHKX,
    CollisionHKX as BaseCollisionHKX,
    ClothHKX as BaseClothHKX,
    RagdollHKX as BaseRagdollHKX,
)
from .physics import PhysicsData, ClothPhysicsData

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    # hkaInterleavedUncompressedAnimation,  # TODO: need class for hk2014
    hkaSplineCompressedAnimation,
    hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapperData]


class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE = hk2014
    root: hkRootLevelContainer
    animation_container: AnimationContainerType


class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE = hk2014
    root: hkRootLevelContainer
    skeleton: SkeletonType
