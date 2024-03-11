"""TODO: Bloodborne/DS3 cloth and ragdoll files have no wrappers."""

from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX"]

from soulstruct_havok.types import hk2014
from soulstruct_havok.types.hk2014 import *
from soulstruct_havok.wrappers.base import *

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    # hkaInterleavedUncompressedAnimation,  # TODO: need class for hk2014
    hkaSplineCompressedAnimation,
    hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]


class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE = hk2014
    root: hkRootLevelContainer
    animation_container: AnimationContainerType


class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE = hk2014
    root: hkRootLevelContainer
    skeleton: SkeletonType
