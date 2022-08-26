from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpConstraintData import hkpConstraintData


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
