from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hclConstraintSet import hclConstraintSet
from .hclStandardLinkConstraintSetLink import hclStandardLinkConstraintSetLink


@dataclass(slots=True, eq=False, repr=False)
class hclStandardLinkConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4078551462

    local_members = (
        Member(40, "links", hkArray(hclStandardLinkConstraintSetLink, hsh=1647365312)),
    )
    members = hclConstraintSet.members + local_members

    links: list[hclStandardLinkConstraintSetLink]
