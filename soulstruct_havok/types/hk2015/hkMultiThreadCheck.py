from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkMultiThreadCheck(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "threadId", hkUint32, MemberFlags.NotSerializable),
        Member(4, "stackTraceId", _int, MemberFlags.NotSerializable),
        Member(8, "markCount", hkUint16, MemberFlags.NotSerializable),
        Member(10, "markBitStack", hkUint16, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = local_members

    threadId: int
    stackTraceId: int
    markCount: int
    markBitStack: int
