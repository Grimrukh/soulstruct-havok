from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hclBufferDefinition import hclBufferDefinition


@dataclass(slots=True, eq=False, repr=False)
class hclScratchBufferDefinition(hclBufferDefinition):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2944427578

    local_members = (
        Member(80, "triangleIndices", hkArray(hkUint16, hsh=3431155310)),
        Member(96, "storeNormals", hkBool),
        Member(97, "storeTangentsAndBiTangents", hkBool),
    )
    members = hclBufferDefinition.members + local_members

    triangleIndices: list[int]
    storeNormals: bool
    storeTangentsAndBiTangents: bool
