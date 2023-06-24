from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkpEntitySpuCollisionCallback(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "util", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(4, "capacity", hkUint16, MemberFlags.NotSerializable),
        Member(6, "eventFilter", hkUint8),
        Member(7, "userFilter", hkUint8),
    )
    members = local_members

    util: None
    capacity: int
    eventFilter: int
    userFilter: int
