from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hclOperator import hclOperator


@dataclass(slots=True, eq=False, repr=False)
class hclUpdateAllVertexFramesOperator(hclOperator):
    alignment = 8
    byte_size = 184
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3765729381
    __version = 3

    local_members = (
        Member(72, "vertToNormalID", hkArray(hkUint16, hsh=3431155310)),
        Member(88, "triangleFlips", hkArray(hkUint8, hsh=2331026425)),
        Member(104, "referenceVertices", hkArray(hkUint16, hsh=3431155310)),
        Member(120, "tangentEdgeCosAngle", hkArray(hkReal, hsh=2219021489)),
        Member(136, "tangentEdgeSinAngle", hkArray(hkReal, hsh=2219021489)),
        Member(152, "biTangentFlip", hkArray(hkReal, hsh=2219021489)),
        Member(168, "bufferIdx", hkUint32),
        Member(172, "numUniqueNormalIDs", hkUint32),
        Member(176, "updateNormals", hkBool),
        Member(177, "updateTangents", hkBool),
        Member(178, "updateBiTangents", hkBool),
    )
    members = hclOperator.members + local_members

    vertToNormalID: list[int]
    triangleFlips: list[int]
    referenceVertices: list[int]
    tangentEdgeCosAngle: list[float]
    tangentEdgeSinAngle: list[float]
    biTangentFlip: list[float]
    bufferIdx: int
    numUniqueNormalIDs: int
    updateNormals: bool
    updateTangents: bool
    updateBiTangents: bool
