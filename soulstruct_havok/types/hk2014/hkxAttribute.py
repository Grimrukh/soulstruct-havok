from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


class hkxAttribute(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "value", Ptr(hkReferencedObject)),
    )
    members = local_members

    name: str
    value: hkReferencedObject
