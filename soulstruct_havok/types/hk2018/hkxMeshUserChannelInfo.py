from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkxAttributeHolder import hkxAttributeHolder


@dataclass(slots=True, eq=False, repr=False)
class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkxMesh::UserChannelInfo"

    local_members = (
        Member(40, "name", hkStringPtr),
        Member(48, "className", hkStringPtr),
    )
    members = hkxAttributeHolder.members + local_members

    name: hkStringPtr
    className: hkStringPtr
