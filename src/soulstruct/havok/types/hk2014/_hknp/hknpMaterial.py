from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hknpMaterialTriggerType import hknpMaterialTriggerType
from .hknpMaterialCombinePolicy import hknpMaterialCombinePolicy
from .hknpMaterialMassChangerCategory import hknpMaterialMassChangerCategory
from .hknpSurfaceVelocity import hknpSurfaceVelocity


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpMaterial(hk):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "isExclusive", hkUint32),
        Member(12, "flags", hkInt32),
        Member(16, "triggerType", hkEnum(hknpMaterialTriggerType, hkUint8)),
        Member(17, "triggerManifoldTolerance", hkUFloat8),
        Member(18, "dynamicFriction", hkHalf16),
        Member(20, "staticFriction", hkHalf16),
        Member(22, "restitution", hkHalf16),
        Member(24, "frictionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8)),
        Member(25, "restitutionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8)),
        Member(26, "weldingTolerance", hkHalf16),
        Member(28, "maxContactImpulse", hkReal),
        Member(32, "fractionOfClippedImpulseToApply", hkReal),
        Member(36, "massChangerCategory", hkEnum(hknpMaterialMassChangerCategory, hkUint8)),
        Member(38, "massChangerHeavyObjectFactor", hkHalf16),
        Member(40, "softContactForceFactor", hkHalf16),
        Member(42, "softContactDampFactor", hkHalf16),
        Member(44, "softContactSeperationVelocity", hkUFloat8),
        Member(48, "surfaceVelocity", Ptr(hknpSurfaceVelocity)),
        Member(56, "disablingCollisionsBetweenCvxCvxDynamicObjectsDistance", hkHalf16),
        Member(64, "userData", hkUint64),
        Member(72, "isShared", hkBool),
    )
    members = local_members

    name: str
    isExclusive: int
    flags: int
    triggerType: int
    triggerManifoldTolerance: hkUFloat8
    dynamicFriction: hkHalf16
    staticFriction: hkHalf16
    restitution: hkHalf16
    frictionCombinePolicy: int
    restitutionCombinePolicy: int
    weldingTolerance: hkHalf16
    maxContactImpulse: float
    fractionOfClippedImpulseToApply: float
    massChangerCategory: int
    massChangerHeavyObjectFactor: hkHalf16
    softContactForceFactor: hkHalf16
    softContactDampFactor: hkHalf16
    softContactSeperationVelocity: hkUFloat8
    surfaceVelocity: hknpSurfaceVelocity
    disablingCollisionsBetweenCvxCvxDynamicObjectsDistance: hkHalf16
    userData: int
    isShared: bool
