from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclBoneSpaceDeformerLocalBlockP(hk):
    alignment = 16
    byte_size = 256
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2451926677
    __real_name = "hclBoneSpaceDeformer::LocalBlockP"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkVector4, 16)),
    )
    members = local_members

    localPosition: tuple[hkVector4]
