from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkRefCountedPropertiesEntry(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "object", Ptr(hkReferencedObject)),
        Member(8, "key", hkUint16),
        Member(10, "flags", hkUint16),
    )
    members = local_members

    object: hkReferencedObject
    key: int
    flags: int
