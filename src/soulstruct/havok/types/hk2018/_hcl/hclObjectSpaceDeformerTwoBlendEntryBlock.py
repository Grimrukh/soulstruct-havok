from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclObjectSpaceDeformerTwoBlendEntryBlock(hk):
    alignment = 2
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2865152819
    __real_name = "hclObjectSpaceDeformer::TwoBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 32)),
        Member(96, "boneWeights", hkGenericStruct(hkUint8, 32)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint8]
