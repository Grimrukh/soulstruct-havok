from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclBoneSpaceDeformerTwoBlendEntryBlock(hk):
    alignment = 2
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2640620584
    __real_name = "hclBoneSpaceDeformer::TwoBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 8)),
        Member(16, "boneIndices", hkGenericStruct(hkUint16, 16)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
