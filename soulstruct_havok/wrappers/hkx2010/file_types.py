from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX"]

from soulstruct_havok.types import hk2010
from soulstruct_havok.types.hk2010 import *
from soulstruct_havok.wrappers.base import *
from soulstruct_havok.wrappers.base.file_types import (
    AnimationHKX as BaseAnimationHKX,
    SkeletonHKX as BaseSkeletonHKX,
    CollisionHKX as BaseCollisionHKX,
    ClothHKX as BaseClothHKX,
    RagdollHKX as BaseRagdollHKX,
)

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapperData]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]


class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer
    animation_container: AnimationContainerType


class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer
    skeleton: SkeletonType


class CollisionHKX(BaseCollisionHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer
    physics_data: PhysicsDataType


class ClothHKX(BaseClothHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem]


class RagdollHKX(BaseRagdollHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer
    standard_skeleton: SkeletonType
    ragdoll_skeleton: SkeletonType
    physics_data: PhysicsDataType
    ragdoll_to_standard_skeleton_mapper: SkeletonMapperType
    standard_to_ragdoll_skeleton_mapper: SkeletonMapperType