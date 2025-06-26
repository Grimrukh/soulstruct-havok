from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpConstraintAtom import hkpConstraintAtom
from .hkpConstraintMotor import hkpConstraintMotor


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpAngMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(2, "isEnabled", hkBool),
        Member(3, "motorAxis", hkUint8),
        Member(4, "initializedOffset", hkInt16, MemberFlags.NotSerializable),
        Member(6, "previousTargetAngleOffset", hkInt16, MemberFlags.NotSerializable),
        Member(8, "correspondingAngLimitSolverResultOffset", hkInt16, MemberFlags.NotSerializable),
        Member(12, "targetAngle", hkReal),
        Member(16, "motor", Ptr(hkpConstraintMotor)),
        Member(24, "padding", hkStruct(hkUint8, 12), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: bool
    motorAxis: int
    initializedOffset: int
    previousTargetAngleOffset: int
    correspondingAngLimitSolverResultOffset: int
    targetAngle: float
    motor: hkpConstraintMotor
    padding: tuple[int, ...]
