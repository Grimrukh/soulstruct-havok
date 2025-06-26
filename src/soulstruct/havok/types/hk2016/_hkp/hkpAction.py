from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpAction(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(16, "world", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
        Member(24, "island", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
        Member(32, "userData", hkUlong, MemberFlags.Protected),
        Member(40, "name", hkStringPtr, MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    world: None = None
    island: None = None
    userData: int
    name: str
