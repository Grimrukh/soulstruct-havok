from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkpWrappedConstraintData import hkpWrappedConstraintData
from .hkpBridgeAtoms import hkpBridgeAtoms


@dataclass(slots=True, eq=False, repr=False)
class hkpBreakableConstraintData(hkpWrappedConstraintData):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1399430718
    __version = 2

    local_members = (
        Member(32, "atoms", hkpBridgeAtoms),
        Member(64, "childRuntimeSize", hkUint16, MemberFlags.NotSerializable),
        Member(66, "childNumSolverResults", hkUint16, MemberFlags.NotSerializable),
        Member(68, "solverResultLimit", hkReal),
        Member(72, "removeWhenBroken", hkBool),
        Member(73, "revertBackVelocityOnBreak", hkBool),
    )
    members = hkpWrappedConstraintData.members + local_members

    atoms: hkpBridgeAtoms
    childRuntimeSize: int
    childNumSolverResults: int
    solverResultLimit: float
    removeWhenBroken: bool
    revertBackVelocityOnBreak: bool
