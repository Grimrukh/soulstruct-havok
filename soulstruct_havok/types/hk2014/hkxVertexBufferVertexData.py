from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkxVertexBufferVertexData(hk):
    alignment = 16
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(0, "vectorData", hkArray(hkUint32)),
        Member(16, "floatData", hkArray(hkUint32)),
        Member(32, "uint32Data", hkArray(hkUint32)),
        Member(48, "uint16Data", hkArray(hkUint16)),
        Member(64, "uint8Data", hkArray(hkUint8)),
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
