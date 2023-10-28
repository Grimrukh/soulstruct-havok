from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkBitFieldStorage(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "words", hkArray(hkUint32, hsh=1109639201)),
        Member(16, "numBits", _int),
    )
    members = local_members

    words: list[int]
    numBits: int

    __templates = (
        TemplateType("tStorage", type=hkArray(hkUint32, hsh=1109639201)),
    )
