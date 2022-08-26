from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


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

    world: hkReflectDetailOpaque
    island: hkReflectDetailOpaque
    userData: int
    name: str
