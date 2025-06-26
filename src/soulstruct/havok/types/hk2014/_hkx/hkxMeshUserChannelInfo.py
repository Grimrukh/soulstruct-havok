from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxAttributeHolder import hkxAttributeHolder


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(32, "name", hkStringPtr),
        Member(40, "className", hkStringPtr),
    )
    members = hkxAttributeHolder.members + local_members

    name: str
    className: str
