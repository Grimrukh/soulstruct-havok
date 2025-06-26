from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpConstraintAtom import hkpConstraintAtom


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpTwistLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "twistAxis", hkUint8),
        Member(4, "refAxis", hkUint8),
        Member(8, "minAngle", hkReal),
        Member(12, "maxAngle", hkReal),
        Member(16, "angularLimitsTauFactor", hkReal),
        Member(20, "angularLimitsDampFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    twistAxis: int
    refAxis: int
    minAngle: float
    maxAngle: float
    angularLimitsTauFactor: float
    angularLimitsDampFactor: float
