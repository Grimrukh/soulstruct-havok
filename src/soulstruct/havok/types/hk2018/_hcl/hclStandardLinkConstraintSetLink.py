from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclStandardLinkConstraintSetLink(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2334495902
    __real_name = "hclStandardLinkConstraintSet::Link"

    local_members = (
        Member(0, "particleA", hkUint16),
        Member(2, "particleB", hkUint16),
        Member(4, "restLength", hkReal),
        Member(8, "stiffness", hkReal),
    )
    members = local_members

    particleA: int
    particleB: int
    restLength: float
    stiffness: float
