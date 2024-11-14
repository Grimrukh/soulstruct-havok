from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX"]

import logging
import typing as tp
from dataclasses import dataclass

from soulstruct_havok.packfile.structs import PackfileHeaderInfo, PackFileVersion
from soulstruct_havok.types import hk550
from soulstruct_havok.types.hk550 import *
from soulstruct_havok.fromsoft.base import *

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaSkeletalAnimation, hkaAnimationBinding,
    hkaInterleavedSkeletalAnimation, hkaSplineSkeletalAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]

_LOGGER = logging.getLogger("soulstruct_havok")


@dataclass(slots=True, repr=False)
class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE = hk550
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None

    @classmethod
    def get_default_hkx_kwargs(cls) -> dict[str, tp.Any]:
        kwargs = super(AnimationHKX, cls).get_default_hkx_kwargs()
        kwargs |= dict(
            packfile_header_info=PackfileHeaderInfo(
                header_version=PackFileVersion.Version0x05,
                pointer_size=4,
                is_little_endian=False,
                reuse_padding_optimization=1,
                contents_version_string=hk550.VERSION,
                flags=0,
                header_extension=None,
            )
        )
        return kwargs

    def get_spline_hkx(self) -> AnimationHKX:
        """Uses Horkrux's compiled converter to convert interleaved HKX to spline HKX.

        Returns an entire new instance of this class.
        """
        raise TypeError(
            "Spline conversion not implemented for Havok 5.5.0 animations as Demon's Souls does not use them."
        )


@dataclass(slots=True, repr=False)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE = hk550
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


@dataclass(slots=True, repr=False)
class CollisionHKX(BaseCollisionHKX):
    TYPES_MODULE = hk550
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


@dataclass(slots=True, repr=False)
class ClothHKX(BaseClothHKX):
    TYPES_MODULE = hk550
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


@dataclass(slots=True, repr=False)
class RagdollHKX(BaseRagdollHKX):
    TYPES_MODULE = hk550
    root: hkRootLevelContainer = None
    animation_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    animation_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapperType = None
