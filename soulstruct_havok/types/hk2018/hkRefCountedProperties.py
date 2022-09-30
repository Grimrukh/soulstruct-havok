from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *

from .hkRefCountedPropertiesEntry import hkRefCountedPropertiesEntry


class hkRefCountedProperties(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2638108928
    __version = 2

    local_members = (
        Member(24, "entries", hkArray(hkRefCountedPropertiesEntry, hsh=3661886975), MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    entries: list[hkRefCountedPropertiesEntry]