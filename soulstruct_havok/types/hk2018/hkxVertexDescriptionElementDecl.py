from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkxVertexDescriptionDataType import hkxVertexDescriptionDataType
from .hkxVertexDescriptionDataUsage import hkxVertexDescriptionDataUsage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxVertexDescriptionElementDecl(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4
    __real_name = "hkxVertexDescription::ElementDecl"

    local_members = (
        Member(0, "byteOffset", hkUint32),
        Member(4, "type", hkEnum(hkxVertexDescriptionDataType, hkUint16)),
        Member(6, "usage", hkEnum(hkxVertexDescriptionDataUsage, hkUint16)),
        Member(8, "byteStride", hkUint32),
        Member(12, "numElements", hkUint8),
        Member(16, "channelID", hkStringPtr),
    )
    members = local_members

    byteOffset: int
    type: hkxVertexDescriptionDataType
    usage: hkxVertexDescriptionDataUsage
    byteStride: int
    numElements: int
    channelID: hkStringPtr
