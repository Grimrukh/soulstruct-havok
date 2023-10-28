from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkPackedVector3 import hkPackedVector3


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclObjectSpaceDeformerLocalBlockP(hk):
    alignment = 8
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1716201389
    __version = 1
    __real_name = "hclObjectSpaceDeformer::LocalBlockP"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkPackedVector3, 16)),
    )
    members = local_members

    localPosition: tuple[hkPackedVector3]
