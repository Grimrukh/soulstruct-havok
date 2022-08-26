from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


class hkpBroadPhaseHandle(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "id", hkUint32, MemberFlags.NotSerializable),
    )
    members = local_members

    id: int
