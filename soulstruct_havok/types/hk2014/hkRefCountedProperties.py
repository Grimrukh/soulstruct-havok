from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkRefCountedPropertiesEntry import hkRefCountedPropertiesEntry


@dataclass(slots=True, eq=False, repr=False)
class hkRefCountedProperties(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2086094951
    __version = 1

    local_members = (
        Member(0, "entries", hkArray(hkRefCountedPropertiesEntry)),
    )
    members = local_members

    entries: list[hkRefCountedPropertiesEntry]
