from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkSweptTransform import hkSweptTransform


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMotionState(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "transform", hkTransform),
        Member(64, "sweptTransform", hkSweptTransform),
        Member(144, "deltaAngle", hkVector4),
        Member(160, "objectRadius", hkReal),
        Member(164, "linearDamping", hkHalf16),
        Member(166, "angularDamping", hkHalf16),
        Member(168, "timeFactor", hkHalf16),
        Member(170, "maxLinearVelocity", hkUint8),
        Member(171, "maxAngularVelocity", hkUint8),
        Member(172, "deactivationClass", hkUint8),
    )
    members = local_members

    transform: hkTransform
    sweptTransform: hkSweptTransform
    deltaAngle: Vector4
    objectRadius: float
    linearDamping: hkHalf16
    angularDamping: hkHalf16
    timeFactor: hkHalf16
    maxLinearVelocity: int
    maxAngularVelocity: int
    deactivationClass: int
