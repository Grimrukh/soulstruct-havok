from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom


@dataclass(slots=True, eq=False, repr=False)
class hkp2dAngConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "freeRotationAxis", hkUint8),
        Member(3, "padding", hkStruct(hkUint8, 12), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    freeRotationAxis: int
    padding: tuple[int, ...]
