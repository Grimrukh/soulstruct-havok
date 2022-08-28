from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


class hkpEntitySmallArraySerializeOverrideType(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "data", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(4, "size", hkUint16),
        Member(6, "capacityAndFlags", hkUint16),
    )
    members = local_members

    data: None
    size: int
    capacityAndFlags: int