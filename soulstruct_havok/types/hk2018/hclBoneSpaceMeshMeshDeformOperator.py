from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hclOperator import hclOperator
from .hclBoneSpaceMeshMeshDeformOperatorScaleNormalBehaviour import hclBoneSpaceMeshMeshDeformOperatorScaleNormalBehaviour
from .hclBoneSpaceDeformer import hclBoneSpaceDeformer


@dataclass(slots=True, eq=False, repr=False)
class hclBoneSpaceMeshMeshDeformOperator(hclOperator):
    alignment = 8
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(72, "inputBufferIdx", hkUint32),
        Member(76, "outputBufferIdx", hkUint32),
        Member(
            80,
            "scaleNormalBehaviour",
            hkEnum(hclBoneSpaceMeshMeshDeformOperatorScaleNormalBehaviour, hkUint32),
        ),
        Member(88, "inputTrianglesSubset", hkArray(hkUint16, hsh=3431155310)),
        Member(104, "boneSpaceDeformer", hclBoneSpaceDeformer),
    )
    members = hclOperator.members + local_members

    inputBufferIdx: int
    outputBufferIdx: int
    scaleNormalBehaviour: hclBoneSpaceMeshMeshDeformOperatorScaleNormalBehaviour
    inputTrianglesSubset: list[int]
    boneSpaceDeformer: hclBoneSpaceDeformer
