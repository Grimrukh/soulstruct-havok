from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxIndexBufferIndexType import hkxIndexBufferIndexType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxIndexBuffer(hkReferencedObject):
    alignment = 8
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(16, "indexType", hkEnum(hkxIndexBufferIndexType, hkInt8)),
        Member(24, "indices16", hkArray(hkUint16)),
        Member(40, "indices32", hkArray(hkUint32, hsh=4255738572)),
        Member(56, "vertexBaseOffset", hkUint32),
        Member(60, "length", hkUint32),
    )
    members = hkReferencedObject.members + local_members

    indexType: hkxIndexBufferIndexType
    indices16: list[int]
    indices32: list[int]
    vertexBaseOffset: int
    length: int
