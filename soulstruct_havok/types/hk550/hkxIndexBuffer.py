from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkxIndexBufferIndexType import hkxIndexBufferIndexType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxIndexBuffer(hkReferencedObject):
    alignment = 16
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "indexType", hkEnum(hkxIndexBufferIndexType, hkInt8)),
        Member(12, "indices16", hkArray(hkUint16)),
        Member(24, "indices32", hkArray(hkUint32)),
        Member(36, "vertexBaseOffset", hkUint32),
        Member(40, "length", hkUint32),
    )
    members = hkReferencedObject.members + local_members

    indexType: int
    indices16: list[int]
    indices32: list[int]
    vertexBaseOffset: int
    length: int
