from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .._hkp.hkpConstraintData import hkpConstraintData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpConstraintCinfo(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(0, "constraintData", Ptr(hkpConstraintData)),
        Member(8, "bodyA", hkUint32),
        Member(12, "bodyB", hkUint32),
        Member(16, "flags", hkFlags(hkUint8)),
    )
    members = local_members

    constraintData: hkpConstraintData
    bodyA: int
    bodyB: int
    flags: int
