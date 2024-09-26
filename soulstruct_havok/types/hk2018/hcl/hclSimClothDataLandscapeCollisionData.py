from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclSimClothDataLandscapeCollisionData(hk):
    alignment = 4
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hclSimClothData::LandscapeCollisionData"

    local_members = (
        Member(0, "landscapeRadius", hkReal),
        Member(4, "enableStuckParticleDetection", hkBool),
        Member(8, "stuckParticlesStretchFactorSq", hkReal),
        Member(12, "pinchDetectionEnabled", hkBool),
        Member(13, "pinchDetectionPriority", hkInt8),
        Member(16, "pinchDetectionRadius", hkReal),
        Member(20, "collisionTolerance", hkReal),
    )
    members = local_members

    landscapeRadius: float
    enableStuckParticleDetection: bool
    stuckParticlesStretchFactorSq: float
    pinchDetectionEnabled: bool
    pinchDetectionPriority: int
    pinchDetectionRadius: float
    collisionTolerance: float
