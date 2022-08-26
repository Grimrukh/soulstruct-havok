from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


class hkpEntitySmallArraySerializeOverrideType(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpEntity::SmallArraySerializeOverrideType"

    local_members = (
        Member(0, "data", Ptr(_void), MemberFlags.NotSerializable),
        Member(8, "size", hkUint16),
        Member(10, "capacityAndFlags", hkUint16),
    )
    members = local_members

    data: _void
    size: int
    capacityAndFlags: int
