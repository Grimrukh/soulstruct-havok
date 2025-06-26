from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpCdBody import hkpCdBody
from .hkpTypedBroadPhaseHandle import hkpTypedBroadPhaseHandle
from .hkpCollidableBoundingVolumeData import hkpCollidableBoundingVolumeData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpCollidable(hkpCdBody):
    alignment = 8
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(32, "ownerOffset", hkInt8, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(33, "forceCollideOntoPpu", hkUint8),
        Member(34, "shapeSizeOnSpu", hkUint16, MemberFlags.NotSerializable),
        Member(36, "broadPhaseHandle", hkpTypedBroadPhaseHandle),
        Member(48, "boundingVolumeData", hkpCollidableBoundingVolumeData, MemberFlags.NotSerializable),
        Member(104, "allowedPenetrationDepth", hkReal),
    )
    members = hkpCdBody.members + local_members

    ownerOffset: int
    forceCollideOntoPpu: int
    shapeSizeOnSpu: int
    broadPhaseHandle: hkpTypedBroadPhaseHandle
    boundingVolumeData: hkpCollidableBoundingVolumeData
    allowedPenetrationDepth: float
