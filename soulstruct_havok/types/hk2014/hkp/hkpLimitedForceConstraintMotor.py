from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpConstraintMotor import hkpConstraintMotor


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpLimitedForceConstraintMotor(hkpConstraintMotor):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(24, "minForce", hkReal),
        Member(28, "maxForce", hkReal),
    )
    members = hkpConstraintMotor.members + local_members

    minForce: float
    maxForce: float
