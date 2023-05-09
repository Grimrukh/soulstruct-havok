from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom
from .hkpConstraintMotor import hkpConstraintMotor


@dataclass(slots=True, eq=False, repr=False)
class hkpRagdollMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(2, "isEnabled", hkBool),
        Member(4, "initializedOffset", hkInt16, MemberFlags.NotSerializable),
        Member(6, "previousTargetAnglesOffset", hkInt16, MemberFlags.NotSerializable),
        Member(16, "target_bRca", hkMatrix3),
        Member(64, "motors", hkGenericStruct(Ptr(hkpConstraintMotor, hsh=1039430764), 3)),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: bool
    initializedOffset: int
    previousTargetAnglesOffset: int
    target_bRca: hkMatrix3
    motors: tuple[hkpConstraintMotor]
