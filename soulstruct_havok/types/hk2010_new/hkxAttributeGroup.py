from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxAttribute import hkxAttribute


class hkxAttributeGroup(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "attributes", hkArray(hkxAttribute)),
    )
    members = local_members

    name: str
    attributes: list[hkxAttribute]
