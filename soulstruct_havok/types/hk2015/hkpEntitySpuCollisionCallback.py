from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkpEntitySpuCollisionCallback(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkpEntity::SpuCollisionCallback"

    local_members = (
        Member(0, "util", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(8, "capacity", hkUint16, MemberFlags.NotSerializable),
        Member(10, "eventFilter", hkUint8),
        Member(11, "userFilter", hkUint8),
    )
    members = local_members

    util: hkReflectDetailOpaque
    capacity: int
    eventFilter: int
    userFilter: int
