from __future__ import annotations

__all__ = [
    "AnimationHKX",
    "SkeletonHKX",
    "AnimationContainerType",
    "SkeletonType",
    "SkeletonMapperType",
]

import typing as tp
from dataclasses import dataclass

from soulstruct_havok.types import hk2018
from soulstruct_havok.types.hk2018 import *
from soulstruct_havok.wrappers.base import *

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]


@dataclass(slots=True)
class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE: tp.ClassVar = hk2018
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None


@dataclass(slots=True)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE: tp.ClassVar = hk2018
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None
