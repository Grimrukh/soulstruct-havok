from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hknpShape import hknpShape
from ..hkLocalFrame import hkLocalFrame


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpBodyCinfo(hk):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(0, "shape", Ptr(hknpShape)),
        Member(8, "reservedBodyId", hkUint32),
        Member(12, "motionId", hkUint32),
        Member(16, "qualityId", hkUint8),
        Member(18, "materialId", hkUint16),
        Member(20, "collisionFilterInfo", hkUint32),
        Member(24, "flags", hkInt32),
        Member(28, "collisionLookAheadDistance", hkReal),
        Member(32, "name", hkStringPtr),
        Member(40, "userData", hkUint64),
        Member(48, "position", hkVector4),
        Member(64, "orientation", hkQuaternionf),
        Member(80, "spuFlags", hkFlags(hkUint8)),
        Member(88, "localFrame", Ptr(hkLocalFrame)),
    )
    members = local_members

    shape: hknpShape
    reservedBodyId: int
    motionId: int
    qualityId: int
    materialId: int
    collisionFilterInfo: int
    flags: int
    collisionLookAheadDistance: float
    name: str
    userData: int
    position: Vector4
    orientation: Quaternion
    spuFlags: int
    localFrame: hkLocalFrame
