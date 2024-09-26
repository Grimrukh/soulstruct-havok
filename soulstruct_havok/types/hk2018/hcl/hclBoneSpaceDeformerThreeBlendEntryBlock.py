from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclBoneSpaceDeformerThreeBlendEntryBlock(hk):
    alignment = 2
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hclBoneSpaceDeformer::ThreeBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 5)),
        Member(10, "boneIndices", hkGenericStruct(hkUint16, 15)),
        Member(40, "padding", hkGenericStruct(hkUint8, 8), MemberFlags.NotSerializable),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    padding: tuple[hkUint8]
