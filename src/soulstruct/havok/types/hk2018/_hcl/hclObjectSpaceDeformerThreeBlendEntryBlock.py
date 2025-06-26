from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclObjectSpaceDeformerThreeBlendEntryBlock(hk):
    alignment = 2
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3839925180
    __real_name = "hclObjectSpaceDeformer::ThreeBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 48)),
        Member(128, "boneWeights", hkGenericStruct(hkUint8, 48)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint8]
