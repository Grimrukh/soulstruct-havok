from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkRefCountedPropertiesEntry(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkRefCountedProperties::Entry"

    local_members = (
        Member(0, "object", hkRefPtr(hkReferencedObject)),
        Member(4, "key", hkUint16),
        Member(6, "flags", hkUint16),
    )
    members = local_members

    object: hkReferencedObject
    key: int
    flags: int
