from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hclOperator import hclOperator


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclGatherAllVerticesOperator(hclOperator):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1253355578
    __version = 1

    local_members = (
        Member(72, "vertexInputFromVertexOutput", hkArray(hkInt16, hsh=3571075457)),
        Member(88, "inputBufferIdx", hkUint32),
        Member(92, "outputBufferIdx", hkUint32),
        Member(96, "gatherNormals", hkBool),
        Member(97, "partialGather", hkBool),
    )
    members = hclOperator.members + local_members

    vertexInputFromVertexOutput: list[int]
    inputBufferIdx: int
    outputBufferIdx: int
    gatherNormals: bool
    partialGather: bool
