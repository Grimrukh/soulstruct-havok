from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxVertexDescriptionElementDeclDataType import hkxVertexDescriptionElementDeclDataType
from .hkxVertexDescriptionElementDeclDataUsage import hkxVertexDescriptionElementDeclDataUsage


@dataclass(slots=True, eq=False, repr=False)
class hkxVertexDescriptionElementDecl(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "byteOffset", hkUint32),
        Member(4, "type", hkEnum(hkxVertexDescriptionElementDeclDataType, hkUint16)),
        Member(6, "usage", hkEnum(hkxVertexDescriptionElementDeclDataUsage, hkUint16)),
        Member(8, "byteStride", hkUint32),
        Member(12, "numElements", hkUint8),
    )
    members = local_members

    byteOffset: int
    type: int
    usage: int
    byteStride: int
    numElements: int
