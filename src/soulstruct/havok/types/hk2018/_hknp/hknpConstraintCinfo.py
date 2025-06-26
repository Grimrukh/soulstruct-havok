from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .._hkp.hkpConstraintData import hkpConstraintData
from .hknpBodyId import hknpBodyId


from .hknpConstraintId import hknpConstraintId
from .hknpConstraintGroupId import hknpConstraintGroupId


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpConstraintCinfo(hk):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2157655739
    __version = 5

    local_members = (
        Member(0, "constraintData", hkRefPtr(hkpConstraintData, hsh=717464932)),
        Member(8, "bodyA", hknpBodyId),
        Member(12, "bodyB", hknpBodyId),
        Member(16, "flags", hkFlags(hkUint16)),
        Member(24, "name", hkStringPtr),
        Member(32, "desiredConstraintId", hknpConstraintId),
        Member(36, "constraintGroupId", hknpConstraintGroupId),
    )
    members = local_members

    constraintData: hkpConstraintData
    bodyA: hknpBodyId
    bodyB: hknpBodyId
    flags: hkUint16
    name: hkStringPtr
    desiredConstraintId: hknpConstraintId
    constraintGroupId: hknpConstraintGroupId
