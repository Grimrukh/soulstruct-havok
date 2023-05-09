from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkpAction(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "world", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(12, "island", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(16, "userData", hkUlong),
        Member(20, "name", hkStringPtr),
    )
    members = hkReferencedObject.members + local_members

    world: None
    island: None
    userData: int
    name: str
