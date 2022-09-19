from __future__ import annotations

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *
from .hclObjectSpaceDeformerLocalBlockP import hclObjectSpaceDeformerLocalBlockP
from .hclObjectSpaceDeformerLocalBlockUnpackedP import hclObjectSpaceDeformerLocalBlockUnpackedP
from .hclObjectSpaceMeshMeshDeformOperator import hclObjectSpaceMeshMeshDeformOperator


class hclObjectSpaceMeshMeshDeformPOperator(hclObjectSpaceMeshMeshDeformOperator):
    alignment = 8
    byte_size = 312
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 48181339
    __version = 1

    local_members = (
        Member(280, "localPs", hkArray(hclObjectSpaceDeformerLocalBlockP, hsh=2974961463)),
        Member(296, "localUnpackedPs", hkArray(hclObjectSpaceDeformerLocalBlockUnpackedP)),
    )
    members = hclObjectSpaceMeshMeshDeformOperator.members + local_members

    localPs: list[hclObjectSpaceDeformerLocalBlockP]
    localUnpackedPs: list[hclObjectSpaceDeformerLocalBlockUnpackedP]
