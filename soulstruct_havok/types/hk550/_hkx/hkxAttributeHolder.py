from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxAttributeGroup import hkxAttributeGroup


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxAttributeHolder(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1146766394

    local_members = (
        Member(0, "attributeGroups", SimpleArray(hkxAttributeGroup)),
    )
    members = local_members

    attributeGroups: list[hkxAttributeGroup]
