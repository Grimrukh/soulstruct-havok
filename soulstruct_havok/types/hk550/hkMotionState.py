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
        Member(164, "linearDamping", hkReal),
        Member(168, "angularDamping", hkReal),
        Member(172, "maxLinearVelocity", hkUFloat8),
        Member(173, "maxAngularVelocity", hkUFloat8),
        Member(174, "deactivationClass", hkUint8),
    )
    members = local_members

    transform: hkTransform
    sweptTransform: hkSweptTransform
    deltaAngle: Vector4
    objectRadius: float
    linearDamping: float
    angularDamping: float
    maxLinearVelocity: hkUFloat8
    maxAngularVelocity: hkUFloat8
    deactivationClass: int
