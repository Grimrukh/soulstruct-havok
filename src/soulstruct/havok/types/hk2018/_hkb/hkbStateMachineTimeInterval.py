from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbStateMachineTimeInterval(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkbStateMachine::TimeInterval"

    local_members = (
        Member(0, "enterEventId", hkInt32),
        Member(4, "exitEventId", hkInt32),
        Member(8, "enterTime", hkReal),
        Member(12, "exitTime", hkReal),
    )
    members = local_members

    enterEventId: int
    exitEventId: int
    enterTime: float
    exitTime: float
