from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxAttributeHolder import hkxAttributeHolder
from .hkxNode import hkxNode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxNodeSelectionSet(hkxAttributeHolder):
    alignment = 4
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 361491079

    local_members = (
        Member(8, "selectedNodes", SimpleArray(hkxNode)),
        Member(16, "name", hkStringPtr),
    )
    members = hkxAttributeHolder.members + local_members

    selectedNodes: list[hkxNode]
    name: str
