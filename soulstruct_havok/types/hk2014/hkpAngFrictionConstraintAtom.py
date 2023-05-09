from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom


@dataclass(slots=True, eq=False, repr=False)
class hkpAngFrictionConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "firstFrictionAxis", hkUint8),
        Member(4, "numFrictionAxes", hkUint8),
        Member(8, "maxFrictionTorque", hkReal),
        Member(12, "padding", hkStruct(hkUint8, 4), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    firstFrictionAxis: int
    numFrictionAxes: int
    maxFrictionTorque: float
    padding: tuple[int, ...]
