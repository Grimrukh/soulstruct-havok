from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkPackedVector3 import hkPackedVector3


@dataclass(slots=True, eq=False, repr=False)
class hclObjectSpaceDeformerLocalBlockPNT(hk):
    alignment = 8
    byte_size = 384
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 848274287
    __version = 1
    __real_name = "hclObjectSpaceDeformer::LocalBlockPNT"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkPackedVector3, 16)),
        Member(128, "localNormal", hkGenericStruct(hkPackedVector3, 16)),
        Member(256, "localTangent", hkGenericStruct(hkPackedVector3, 16)),
    )
    members = local_members

    localPosition: tuple[hkPackedVector3]
    localNormal: tuple[hkPackedVector3]
    localTangent: tuple[hkPackedVector3]
