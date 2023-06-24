from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkxIndexBufferIndexType import hkxIndexBufferIndexType


@dataclass(slots=True, eq=False, repr=False)
class hkxIndexBuffer(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(24, "indexType", hkEnum(hkxIndexBufferIndexType, hkInt8)),
        Member(32, "indices16", hkArray(hkUint16)),
        Member(48, "indices32", hkArray(hkUint32, hsh=1109639201)),
        Member(64, "vertexBaseOffset", hkUint32),
        Member(68, "length", hkUint32),
    )
    members = hkReferencedObject.members + local_members

    indexType: hkxIndexBufferIndexType
    indices16: list[int]
    indices32: list[int]
    vertexBaseOffset: int
    length: int
