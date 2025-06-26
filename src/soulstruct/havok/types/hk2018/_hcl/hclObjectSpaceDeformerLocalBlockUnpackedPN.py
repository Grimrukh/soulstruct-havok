from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclObjectSpaceDeformerLocalBlockUnpackedPN(hk):
    alignment = 16
    byte_size = 512
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::LocalBlockUnpackedPN"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkVector4, 16)),
        Member(256, "localNormal", hkGenericStruct(hkVector4, 16)),
    )
    members = local_members

    localPosition: tuple[hkVector4]
    localNormal: tuple[hkVector4]
