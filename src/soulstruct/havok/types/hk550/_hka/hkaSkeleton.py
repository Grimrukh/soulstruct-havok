from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaBone import hkaBone


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeleton(hk):
    alignment = 8
    byte_size = 36
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 860733036

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "parentIndices", SimpleArray(hkInt16)),
        Member(12, "bones", SimpleArray(Ptr(hkaBone))),
        Member(20, "referencePose", SimpleArray(hkQsTransform)),
        Member(28, "floatSlots", SimpleArray(hkStringPtr)),
    )
    members = local_members

    name: str
    parentIndices: list[int]
    bones: list[hkaBone]
    referencePose: list[hkQsTransform]
    floatSlots: list[str]
