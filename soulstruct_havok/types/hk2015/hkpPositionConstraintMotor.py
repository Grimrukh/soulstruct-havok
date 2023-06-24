from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpLimitedForceConstraintMotor import hkpLimitedForceConstraintMotor


@dataclass(slots=True, eq=False, repr=False)
class hkpPositionConstraintMotor(hkpLimitedForceConstraintMotor):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1057998472

    local_members = (
        Member(32, "tau", hkReal),
        Member(36, "damping", hkReal),
        Member(40, "proportionalRecoveryVelocity", hkReal),
        Member(44, "constantRecoveryVelocity", hkReal),
    )
    members = hkpLimitedForceConstraintMotor.members + local_members

    tau: float
    damping: float
    proportionalRecoveryVelocity: float
    constantRecoveryVelocity: float
