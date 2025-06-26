from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpBallSocketChainDataConstraintInfo(hk):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2871959050
    __version = 1
    __real_name = "hkpBallSocketChainData::ConstraintInfo"

    local_members = (
        Member(0, "pivotInA", hkVector4),
        Member(16, "pivotInB", hkVector4),
        Member(32, "flags", hkUint32),
    )
    members = local_members

    pivotInA: hkVector4
    pivotInB: hkVector4
    flags: int
