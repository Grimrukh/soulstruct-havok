from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hclBoneSpaceDeformerLocalBlockP import hclBoneSpaceDeformerLocalBlockP
from .hclBoneSpaceDeformerLocalBlockUnpackedP import hclBoneSpaceDeformerLocalBlockUnpackedP
from .hclBoneSpaceMeshMeshDeformOperator import hclBoneSpaceMeshMeshDeformOperator


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclBoneSpaceMeshMeshDeformPOperator(hclBoneSpaceMeshMeshDeformOperator):
    alignment = 8
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1671229033
    __version = 1

    local_members = (
        Member(192, "localPs", hkArray(hclBoneSpaceDeformerLocalBlockP, hsh=2181080418)),
        Member(208, "localUnpackedPs", hkArray(hclBoneSpaceDeformerLocalBlockUnpackedP)),
    )
    members = hclBoneSpaceMeshMeshDeformOperator.members + local_members

    localPs: list[hclBoneSpaceDeformerLocalBlockP]
    localUnpackedPs: list[hclBoneSpaceDeformerLocalBlockUnpackedP]
