from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMultiThreadCheck(hk):
    alignment = 16
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "threadId", hkUint32, MemberFlags.NotSerializable),
        Member(4, "markCount", hkUint16, MemberFlags.NotSerializable),
        Member(6, "markBitStack", hkUint16, MemberFlags.NotSerializable),
    )
    members = local_members

    threadId: int
    markCount: int
    markBitStack: int
