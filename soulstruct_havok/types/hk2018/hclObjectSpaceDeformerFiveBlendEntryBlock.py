from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclObjectSpaceDeformerFiveBlendEntryBlock(hk):
    alignment = 2
    byte_size = 352
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::FiveBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 80)),
        Member(192, "boneWeights", hkGenericStruct(hkUint16, 80)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint16]
