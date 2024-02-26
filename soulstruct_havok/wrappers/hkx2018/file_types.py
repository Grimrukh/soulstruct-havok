from __future__ import annotations

__all__ = [
    "AnimationHKX",
    "SkeletonHKX",
    # "ClothHKX",
    # "RagdollHKX",
    "AnimationContainerType",
    "SkeletonType",
    "SkeletonMapperType",
]

import typing as tp
from dataclasses import dataclass

from soulstruct_havok.types import hk2018
from soulstruct_havok.types.hk2018 import *
from soulstruct_havok.wrappers.base import *
from soulstruct_havok.wrappers.base.file_types import (
    AnimationHKX as BaseAnimationHKX,
    SkeletonHKX as BaseSkeletonHKX,
    # ClothHKX as BaseClothHKX,
    # RagdollHKX as BaseRagdollHKX,
)

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapperData]


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


# TODO: No `hkpPhysicsData/System` in hk2018.
# @dataclass(slots=True)
# class ClothHKX(BaseClothHKX):
#     TYPES_MODULE: tp.ClassVar = hk2018
#     root: hkRootLevelContainer = None
#     cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


# TODO: No `hkpPhysicsData/System` in hk2018.
# @dataclass(slots=True)
# class RagdollHKX(BaseRagdollHKX):
#     TYPES_MODULE: tp.ClassVar = hk2018
#     root: hkRootLevelContainer = None
#     standard_skeleton: SkeletonType = None
#     ragdoll_skeleton: SkeletonType = None
#     physics_data: PhysicsDataType = None
#     ragdoll_to_standard_skeleton_mapper: SkeletonMapperType = None
#     standard_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
