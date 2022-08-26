from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxAttributeHolder import hkxAttributeHolder


class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 16
    byte_size = 28
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(20, "name", hkStringPtr),
        Member(24, "className", hkStringPtr),
    )
    members = hkxAttributeHolder.members + local_members

    name: str
    className: str
