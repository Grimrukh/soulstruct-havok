from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbEventBase import hkbEventBase


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbEvent(hkbEventBase):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(16, "sender", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkbEventBase.members + local_members

    sender: hkReflectDetailOpaque
