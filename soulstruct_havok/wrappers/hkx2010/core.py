from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX"]

import logging
from dataclasses import dataclass

from soulstruct_havok.types import hk2010
from soulstruct_havok.types.hk2010 import *
from soulstruct_havok.wrappers.base import *

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]

_LOGGER = logging.getLogger("soulstruct_havok")


@dataclass(slots=True, repr=False)
class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None


@dataclass(slots=True, repr=False)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


@dataclass(slots=True, repr=False)
class CollisionHKX(BaseCollisionHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


@dataclass(slots=True, repr=False)
class ClothHKX(BaseClothHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


@dataclass(slots=True, repr=False)
class RagdollHKX(BaseRagdollHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    animation_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    animation_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapperType = None
