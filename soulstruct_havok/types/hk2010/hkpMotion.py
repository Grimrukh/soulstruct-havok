from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkMotionState import hkMotionState
from .hkpMotionMotionType import hkpMotionMotionType


@dataclass(slots=True, eq=False, repr=False)
class hkpMotion(hkReferencedObject):
    alignment = 16
    byte_size = 288
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "type", hkEnum(hkpMotionMotionType, hkUint8)),
        Member(9, "deactivationIntegrateCounter", hkUint8),
        Member(10, "deactivationNumInactiveFrames", hkStruct(hkUint16, 2)),
        Member(16, "motionState", hkMotionState),
        Member(192, "inertiaAndMassInv", hkVector4),
        Member(208, "linearVelocity", hkVector4),
        Member(224, "angularVelocity", hkVector4),
        Member(240, "deactivationRefPosition", hkStruct(hkVector4, 2)),
        Member(272, "deactivationRefOrientation", hkStruct(hkUint32, 2)),
        Member(280, "savedMotion", Ptr(DefType("hkpMotion", lambda: hkpMotion))),
        Member(284, "savedQualityTypeIndex", hkUint16),
        Member(286, "gravityFactor", hkHalf16),
    )
    members = hkReferencedObject.members + local_members

    type: int
    deactivationIntegrateCounter: int
    deactivationNumInactiveFrames: tuple[int, ...]
    motionState: hkMotionState
    inertiaAndMassInv: Vector4
    linearVelocity: Vector4
    angularVelocity: Vector4
    deactivationRefPosition: tuple[hkVector4, ...]
    deactivationRefOrientation: tuple[int, ...]
    savedMotion: hkpMotion
    savedQualityTypeIndex: int
    gravityFactor: hkHalf16
