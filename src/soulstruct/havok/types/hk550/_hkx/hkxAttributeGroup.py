from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxAttribute import hkxAttribute


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxAttributeGroup(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 375898140

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "attributes", SimpleArray(hkxAttribute)),
    )
    members = local_members

    name: str
    attributes: list[hkxAttribute]
