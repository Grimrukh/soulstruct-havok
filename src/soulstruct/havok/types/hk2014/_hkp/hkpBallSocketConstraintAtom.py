from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpConstraintAtom import hkpConstraintAtom
from .hkpBallSocketConstraintAtomSolvingMethod import hkpBallSocketConstraintAtomSolvingMethod


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpBallSocketConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 5

    local_members = (
        Member(2, "solvingMethod", hkEnum(hkpBallSocketConstraintAtomSolvingMethod, hkUint8)),
        Member(3, "bodiesToNotify", hkUint8),
        Member(4, "velocityStabilizationFactor", hkUFloat8),
        Member(5, "enableLinearImpulseLimit", hkBool),
        Member(8, "breachImpulse", hkReal),
        Member(12, "inertiaStabilizationFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    solvingMethod: int
    bodiesToNotify: int
    velocityStabilizationFactor: hkUFloat8
    enableLinearImpulseLimit: bool
    breachImpulse: float
    inertiaStabilizationFactor: float
