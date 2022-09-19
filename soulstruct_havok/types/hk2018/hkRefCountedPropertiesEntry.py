from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *




class hkRefCountedPropertiesEntry(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4078376394
    __real_name = "hkRefCountedProperties::Entry"

    local_members = (
        Member(0, "object", hkRefPtr(hkReferencedObject, hsh=1519938165)),
        Member(8, "key", hkUint16),
        Member(10, "flags", hkUint16),
    )
    members = local_members

    object: hkReferencedObject
    key: int
    flags: int
