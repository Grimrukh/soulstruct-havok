from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkxAttribute(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "value", Ptr(hkReferencedObject)),
    )
    members = local_members

    name: str
    value: hkReferencedObject
