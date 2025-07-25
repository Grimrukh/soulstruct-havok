from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hclObjectSpaceDeformerLocalBlockP import hclObjectSpaceDeformerLocalBlockP
from .hclObjectSpaceDeformerLocalBlockUnpackedP import hclObjectSpaceDeformerLocalBlockUnpackedP
from .hclObjectSpaceMeshMeshDeformOperator import hclObjectSpaceMeshMeshDeformOperator


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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
