from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkHalf16 import hkHalf16
from .hkUFloat8 import hkUFloat8


@dataclass(slots=True, eq=False, repr=False)
class hkMotionState(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(0, "transform", hkTransform, MemberFlags.Protected),
        Member(64, "sweptTransform", hkGenericStruct(hkVector4f, 5), MemberFlags.Protected),
        Member(144, "deltaAngle", hkVector4),
        Member(160, "objectRadius", hkReal),
        Member(164, "linearDamping", hkHalf16),
        Member(166, "angularDamping", hkHalf16),
        Member(168, "timeFactor", hkHalf16),
        Member(170, "maxLinearVelocity", hkUFloat8),
        Member(171, "maxAngularVelocity", hkUFloat8),
        Member(172, "deactivationClass", hkUint8),
    )
    members = local_members

    transform: hkTransform
    sweptTransform: tuple[Vector4]
    deltaAngle: Vector4
    objectRadius: float
    linearDamping: float
    angularDamping: float
    timeFactor: float
    maxLinearVelocity: hkUFloat8
    maxAngularVelocity: hkUFloat8
    deactivationClass: int
