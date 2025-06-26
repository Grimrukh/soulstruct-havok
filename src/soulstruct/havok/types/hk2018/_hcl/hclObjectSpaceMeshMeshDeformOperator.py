from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hclOperator import hclOperator

from .hclObjectSpaceMeshMeshDeformOperatorScaleNormalBehaviour import hclObjectSpaceMeshMeshDeformOperatorScaleNormalBehaviour


from .hclObjectSpaceDeformer import hclObjectSpaceDeformer


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclObjectSpaceMeshMeshDeformOperator(hclOperator):
    alignment = 8
    byte_size = 280
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1

    local_members = (
        Member(72, "inputBufferIdx", hkUint32),
        Member(76, "outputBufferIdx", hkUint32),
        Member(
            80,
            "scaleNormalBehaviour",
            hkEnum(hclObjectSpaceMeshMeshDeformOperatorScaleNormalBehaviour, hkUint32),
        ),
        Member(88, "inputTrianglesSubset", hkArray(hkUint16, hsh=3431155310)),
        Member(104, "triangleFromMeshTransforms", hkArray(hkMatrix4, hsh=3899186074)),
        Member(120, "objectSpaceDeformer", hclObjectSpaceDeformer),
        Member(272, "customSkinDeform", hkBool),
    )
    members = hclOperator.members + local_members

    inputBufferIdx: int
    outputBufferIdx: int
    scaleNormalBehaviour: hclObjectSpaceMeshMeshDeformOperatorScaleNormalBehaviour
    inputTrianglesSubset: list[int]
    triangleFromMeshTransforms: list[hkMatrix4]
    objectSpaceDeformer: hclObjectSpaceDeformer
    customSkinDeform: bool
