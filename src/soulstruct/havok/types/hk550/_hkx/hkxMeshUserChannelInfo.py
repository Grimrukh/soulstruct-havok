from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxAttributeHolder import hkxAttributeHolder


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1693032508

    local_members = (
        Member(8, "name", hkStringPtr),
        Member(12, "className", hkStringPtr),
    )
    members = hkxAttributeHolder.members + local_members

    name: str
    className: str
