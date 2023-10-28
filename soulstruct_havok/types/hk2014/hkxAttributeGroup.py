from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkxAttribute import hkxAttribute


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxAttributeGroup(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "attributes", hkArray(hkxAttribute)),
    )
    members = local_members

    name: str
    attributes: list[hkxAttribute]
