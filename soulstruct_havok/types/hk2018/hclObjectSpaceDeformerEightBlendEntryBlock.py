from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclObjectSpaceDeformerEightBlendEntryBlock(hk):
    alignment = 2
    byte_size = 544
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::EightBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 128)),
        Member(288, "boneWeights", hkGenericStruct(hkUint16, 128)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint16]
