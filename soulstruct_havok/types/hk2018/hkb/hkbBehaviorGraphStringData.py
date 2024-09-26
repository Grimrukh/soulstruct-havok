from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbBehaviorGraphStringData(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3582228406
    __version = 2

    local_members = (
        Member(24, "eventNames", hkArray(hkStringPtr, hsh=271207693)),
        Member(40, "attributeNames", hkArray(hkStringPtr, hsh=271207693)),
        Member(56, "variableNames", hkArray(hkStringPtr, hsh=271207693)),
        Member(72, "characterPropertyNames", hkArray(hkStringPtr, hsh=271207693)),
        Member(88, "animationNames", hkArray(hkStringPtr, hsh=271207693)),
    )
    members = hkReferencedObject.members + local_members

    eventNames: list[hkStringPtr]
    attributeNames: list[hkStringPtr]
    variableNames: list[hkStringPtr]
    characterPropertyNames: list[hkStringPtr]
    animationNames: list[hkStringPtr]
