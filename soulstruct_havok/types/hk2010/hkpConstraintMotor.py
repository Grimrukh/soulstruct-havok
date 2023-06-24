from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintMotorMotorType import hkpConstraintMotorMotorType


@dataclass(slots=True, eq=False, repr=False)
class hkpConstraintMotor(hkReferencedObject):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "type", hkEnum(hkpConstraintMotorMotorType, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    type: int
