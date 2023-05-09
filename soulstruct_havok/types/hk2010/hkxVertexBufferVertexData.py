from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkxVertexBufferVertexData(hk):
    alignment = 16
    byte_size = 84
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "vectorData", hkArray(hkVector4)),
        Member(12, "floatData", hkArray(hkReal)),
        Member(24, "uint32Data", hkArray(hkUint32)),
        Member(36, "uint16Data", hkArray(hkUint16)),
        Member(48, "uint8Data", hkArray(hkUint8)),
        Member(60, "numVerts", hkUint32),
        Member(64, "vectorStride", hkUint32),
        Member(68, "floatStride", hkUint32),
        Member(72, "uint32Stride", hkUint32),
        Member(76, "uint16Stride", hkUint32),
        Member(80, "uint8Stride", hkUint32),
    )
    members = local_members

    vectorData: list[hkVector4]
    floatData: list[float]
    uint32Data: list[int]
    uint16Data: list[int]
    uint8Data: list[int]
    numVerts: int
    vectorStride: int
    floatStride: int
    uint32Stride: int
    uint16Stride: int
    uint8Stride: int
