from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkxVertexBufferVertexData(hk):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2
    __real_name = "hkxVertexBuffer::VertexData"

    local_members = (
        Member(0, "vectorData", hkArray(_unsigned_int)),
        Member(16, "floatData", hkArray(_unsigned_int)),
        Member(32, "uint32Data", hkArray(hkUint32, hsh=4255738572)),
        Member(48, "uint16Data", hkArray(hkUint16)),
        Member(64, "uint8Data", hkArray(hkUint8, hsh=2877151166)),
        Member(80, "numVerts", hkUint32),
        Member(84, "vectorStride", hkUint32),
        Member(88, "floatStride", hkUint32),
        Member(92, "uint32Stride", hkUint32),
        Member(96, "uint16Stride", hkUint32),
        Member(100, "uint8Stride", hkUint32),
    )
    members = local_members

    vectorData: list[int]
    floatData: list[int]
    uint32Data: list[int]
    uint16Data: list[int]
    uint8Data: list[int]
    numVerts: int
    vectorStride: int
    floatStride: int
    uint32Stride: int
    uint16Stride: int
    uint8Stride: int
