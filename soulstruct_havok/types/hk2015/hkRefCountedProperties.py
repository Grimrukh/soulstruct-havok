from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


from .hkRefCountedPropertiesEntry import hkRefCountedPropertiesEntry


@dataclass(slots=True, eq=False, repr=False)
class hkRefCountedProperties(hkReferencedObject):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(0, "entries", hkArray(hkRefCountedPropertiesEntry), MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    entries: list[hkRefCountedPropertiesEntry]
