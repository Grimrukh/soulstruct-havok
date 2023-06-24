from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hclConstraintSet import hclConstraintSet
from .hclStretchLinkConstraintSetLink import hclStretchLinkConstraintSetLink


@dataclass(slots=True, eq=False, repr=False)
class hclStretchLinkConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2665167600

    local_members = (
        Member(40, "links", hkArray(hclStretchLinkConstraintSetLink, hsh=4260047912)),
    )
    members = hclConstraintSet.members + local_members

    links: list[hclStretchLinkConstraintSetLink]
