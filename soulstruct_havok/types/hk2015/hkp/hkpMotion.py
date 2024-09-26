from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpMotionMotionType import hkpMotionMotionType
from ..hkMotionState import hkMotionState


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpMotion(hkReferencedObject):
    alignment = 16
    byte_size = 320
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 3

    local_members = (
        Member(16, "type", hkEnum(hkpMotionMotionType, hkUint8)),
        Member(17, "deactivationIntegrateCounter", hkUint8),
        Member(18, "deactivationNumInactiveFrames", hkGenericStruct(hkUint16, 2)),
        Member(32, "motionState", hkMotionState),
        Member(208, "inertiaAndMassInv", hkVector4),
        Member(224, "linearVelocity", hkVector4),
        Member(240, "angularVelocity", hkVector4),
        Member(256, "deactivationRefPosition", hkGenericStruct(hkVector4, 2)),
        Member(288, "deactivationRefOrientation", hkGenericStruct(hkUint32, 2)),
        Member(296, "savedMotion", Ptr(DefType("hkpMotion", lambda: hkpMotion))),
        Member(304, "savedQualityTypeIndex", hkUint16),
        Member(306, "gravityFactor", hkHalf16),
    )
    members = hkReferencedObject.members + local_members

    type: int
    deactivationIntegrateCounter: int
    deactivationNumInactiveFrames: tuple[int, int]
    motionState: hkMotionState
    inertiaAndMassInv: Vector4
    linearVelocity: Vector4
    angularVelocity: Vector4
    deactivationRefPosition: tuple[Vector4, Vector4]
    deactivationRefOrientation: tuple[int, int]
    savedMotion: hkpMotion | None
    savedQualityTypeIndex: int
    gravityFactor: hkHalf16
