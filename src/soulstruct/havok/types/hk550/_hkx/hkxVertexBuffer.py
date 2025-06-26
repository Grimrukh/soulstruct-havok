from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxVertexFormat import hkxVertexFormat


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxVertexBuffer(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1460016212

    local_members = (
        Member(0, "vertexDataClass", Ptr(hk)),
        Member(4, "vertexData", SimpleArray(_void)),
        Member(12, "format", Ptr(hkxVertexFormat)),
    )
    members = local_members

    vertexDataClass: hk
    vertexData: list[_void]
    format: hkxVertexFormat
