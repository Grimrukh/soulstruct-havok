from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpCdBody import hkpCdBody
from .hkpTypedBroadPhaseHandle import hkpTypedBroadPhaseHandle
from .hkpCollidableBoundingVolumeData import hkpCollidableBoundingVolumeData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpCollidable(hkpCdBody):
    alignment = 16
    byte_size = 76
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "ownerOffset", hkInt8, MemberFlags.NotSerializable),
        Member(17, "forceCollideOntoPpu", hkUint8),
        Member(18, "shapeSizeOnSpu", hkUint16, MemberFlags.NotSerializable),
        Member(20, "broadPhaseHandle", hkpTypedBroadPhaseHandle),
        Member(32, "boundingVolumeData", hkpCollidableBoundingVolumeData, MemberFlags.NotSerializable),
        Member(72, "allowedPenetrationDepth", hkReal),
    )
    members = hkpCdBody.members + local_members

    ownerOffset: int
    forceCollideOntoPpu: int
    shapeSizeOnSpu: int
    broadPhaseHandle: hkpTypedBroadPhaseHandle
    boundingVolumeData: hkpCollidableBoundingVolumeData
    allowedPenetrationDepth: float
