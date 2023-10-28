from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpBroadPhaseHandle import hkpBroadPhaseHandle


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpTypedBroadPhaseHandle(hkpBroadPhaseHandle):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(4, "type", hkInt8),
        Member(5, "ownerOffset", hkInt8, MemberFlags.NotSerializable),
        Member(6, "objectQualityType", hkInt8),
        Member(8, "collisionFilterInfo", hkUint32),
    )
    members = hkpBroadPhaseHandle.members + local_members

    type: int
    ownerOffset: int
    objectQualityType: int
    collisionFilterInfo: int
