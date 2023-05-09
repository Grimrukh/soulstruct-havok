from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hclOperator import hclOperator


@dataclass(slots=True, eq=False, repr=False)
class hclCopyVerticesOperator(hclOperator):
    alignment = 8
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2019478703

    local_members = (
        Member(72, "inputBufferIdx", hkUint32),
        Member(76, "outputBufferIdx", hkUint32),
        Member(80, "numberOfVertices", hkUint32),
        Member(84, "startVertexIn", hkUint32),
        Member(88, "startVertexOut", hkUint32),
        Member(92, "copyNormals", hkBool),
    )
    members = hclOperator.members + local_members

    inputBufferIdx: int
    outputBufferIdx: int
    numberOfVertices: int
    startVertexIn: int
    startVertexOut: int
    copyNormals: bool
