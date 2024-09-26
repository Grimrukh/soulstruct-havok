from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbModifier import hkbModifier


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbModifierList(hkbModifier):
    alignment = 8
    byte_size = 120
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 644368847

    local_members = (
        Member(104, "modifiers", hkArray(Ptr(hkbModifier, hsh=2863074375), hsh=1892691435)),
    )
    members = hkbModifier.members + local_members

    modifiers: list[hkbModifier]
