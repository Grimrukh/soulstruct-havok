from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom
from .hkpBallSocketConstraintAtomSolvingMethod import hkpBallSocketConstraintAtomSolvingMethod


@dataclass(slots=True, eq=False, repr=False)
class hkpBallSocketConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "solvingMethod", hkEnum(hkpBallSocketConstraintAtomSolvingMethod, hkUint8)),
        Member(3, "bodiesToNotify", hkUint8),
        Member(4, "velocityStabilizationFactor", hkUint8),
        Member(8, "maxImpulse", hkReal),
        Member(12, "inertiaStabilizationFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    solvingMethod: int
    bodiesToNotify: int
    velocityStabilizationFactor: int
    maxImpulse: float
    inertiaStabilizationFactor: float
