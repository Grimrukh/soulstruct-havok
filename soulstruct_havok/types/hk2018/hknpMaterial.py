from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hknpMaterialTriggerType import hknpMaterialTriggerType
from .hknpMaterialCombinePolicy import hknpMaterialCombinePolicy
from .hknpMaterialMassChangerCategory import hknpMaterialMassChangerCategory
from .hknpSurfaceVelocity import hknpSurfaceVelocity


@dataclass(slots=True, eq=False, repr=False)
class hknpMaterial(hkReferencedObject):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3705778722
    __version = 5

    local_members = (
        Member(32, "name", hkStringPtr),
        Member(40, "isExclusive", hkUint32),
        Member(44, "flags", _int),
        Member(48, "triggerType", hkEnum(hknpMaterialTriggerType, hkUint8)),
        Member(49, "triggerManifoldTolerance", hkUFloat8),
        Member(50, "dynamicFriction", hkHalf16),
        Member(52, "staticFriction", hkHalf16),
        Member(54, "restitution", hkHalf16),
        Member(56, "frictionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8)),
        Member(57, "restitutionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8)),
        Member(60, "weldingTolerance", hkReal),
        Member(64, "maxContactImpulse", hkReal),
        Member(68, "fractionOfClippedImpulseToApply", hkReal),
        Member(72, "massChangerCategory", hkEnum(hknpMaterialMassChangerCategory, hkUint8)),
        Member(74, "massChangerHeavyObjectFactor", hkHalf16),
        Member(76, "softContactForceFactor", hkHalf16),
        Member(78, "softContactDampFactor", hkHalf16),
        Member(80, "softContactSeparationVelocity", hkUFloat8),
        Member(88, "surfaceVelocity", Ptr(hknpSurfaceVelocity)),
        Member(96, "disablingCollisionsBetweenCvxCvxDynamicObjectsDistance", hkHalf16),
        Member(104, "userData", hkUint64),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    isExclusive: int
    flags: int
    triggerType: hknpMaterialTriggerType
    triggerManifoldTolerance: hkUFloat8
    dynamicFriction: float
    staticFriction: float
    restitution: float
    frictionCombinePolicy: hknpMaterialCombinePolicy
    restitutionCombinePolicy: hknpMaterialCombinePolicy
    weldingTolerance: float
    maxContactImpulse: float
    fractionOfClippedImpulseToApply: float
    massChangerCategory: hknpMaterialMassChangerCategory
    massChangerHeavyObjectFactor: float
    softContactForceFactor: float
    softContactDampFactor: float
    softContactSeparationVelocity: hkUFloat8
    surfaceVelocity: hknpSurfaceVelocity
    disablingCollisionsBetweenCvxCvxDynamicObjectsDistance: float
    userData: int
