from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpLimitedForceConstraintMotor import hkpLimitedForceConstraintMotor


@dataclass(slots=True, eq=False, repr=False)
class hkpPositionConstraintMotor(hkpLimitedForceConstraintMotor):
    alignment = 16
    byte_size = 36
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1955574531

    local_members = (
        Member(20, "tau", hkReal),
        Member(24, "damping", hkReal),
        Member(28, "proportionalRecoveryVelocity", hkReal),
        Member(32, "constantRecoveryVelocity", hkReal),
    )
    members = hkpLimitedForceConstraintMotor.members + local_members

    tau: float
    damping: float
    proportionalRecoveryVelocity: float
    constantRecoveryVelocity: float
