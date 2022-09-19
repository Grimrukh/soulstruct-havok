from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hclOperator import hclOperator

from .hclSimpleMeshBoneDeformOperatorTriangleBonePair import hclSimpleMeshBoneDeformOperatorTriangleBonePair



class hclSimpleMeshBoneDeformOperator(hclOperator):
    alignment = 8
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2605270853

    local_members = (
        Member(72, "inputBufferIdx", hkUint32),
        Member(76, "outputTransformSetIdx", hkUint32),
        Member(
            80,
            "triangleBonePairs",
            hkArray(hclSimpleMeshBoneDeformOperatorTriangleBonePair, hsh=121283141),
        ),
        Member(96, "localBoneTransforms", hkArray(hkMatrix4, hsh=3899186074)),
    )
    members = hclOperator.members + local_members

    inputBufferIdx: int
    outputTransformSetIdx: int
    triangleBonePairs: list[hclSimpleMeshBoneDeformOperatorTriangleBonePair]
    localBoneTransforms: list[hkMatrix4]
