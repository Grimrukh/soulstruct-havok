from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclLocalRangeConstraintSetLocalConstraint(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2381122027
    __real_name = "hclLocalRangeConstraintSet::LocalConstraint"

    local_members = (
        Member(0, "particleIndex", hkUint16),
        Member(2, "referenceVertex", hkUint16),
        Member(4, "maximumDistance", hkReal),
        Member(8, "maxNormalDistance", hkReal),
        Member(12, "minNormalDistance", hkReal),
    )
    members = local_members

    particleIndex: int
    referenceVertex: int
    maximumDistance: float
    maxNormalDistance: float
    minNormalDistance: float
