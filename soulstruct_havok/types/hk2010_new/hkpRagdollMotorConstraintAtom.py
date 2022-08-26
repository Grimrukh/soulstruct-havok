from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom
from .Ptr[hkpConstraintMotor], 3 import Ptr[hkpConstraintMotor], 3


class hkpRagdollMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkBool),
        Member(4, "initializedOffset", hkInt16),
        Member(6, "previousTargetAnglesOffset", hkInt16),
        Member(16, "target_bRca", hkMatrix3),
        Member(64, "motors", hkStruct(Ptr(hkpConstraintMotor), 3)),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: bool
    initializedOffset: int
    previousTargetAnglesOffset: int
    target_bRca: hkMatrix3
    motors: tuple[hkpConstraintMotor, ...]
