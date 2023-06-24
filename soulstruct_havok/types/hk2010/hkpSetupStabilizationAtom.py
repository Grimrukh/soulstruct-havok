from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintAtom import hkpConstraintAtom


@dataclass(slots=True, eq=False, repr=False)
class hkpSetupStabilizationAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "enabled", hkBool),
        Member(4, "maxAngle", hkReal),
        Member(8, "padding", hkStruct(hkUint8, 8)),
    )
    members = hkpConstraintAtom.members + local_members

    enabled: bool
    maxAngle: float
    padding: tuple[int, ...]
