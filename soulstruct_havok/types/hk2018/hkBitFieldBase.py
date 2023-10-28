from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkBitFieldStorage import hkBitFieldStorage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkBitFieldBase(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "storage", hkBitFieldStorage, MemberFlags.Protected),
    )
    members = local_members

    storage: hkBitFieldStorage

    __templates = (
        TemplateType("tStorage", type=hkBitFieldStorage),
    )
