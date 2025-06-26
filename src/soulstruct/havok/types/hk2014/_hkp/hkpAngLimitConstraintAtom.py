from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpConstraintAtom import hkpConstraintAtom


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpAngLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "limitAxis", hkUint8),
        Member(4, "minAngle", hkReal),
        Member(8, "maxAngle", hkReal),
        Member(12, "angularLimitsTauFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    limitAxis: int
    minAngle: float
    maxAngle: float
    angularLimitsTauFactor: float
