from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbStateMachineTimeInterval import hkbStateMachineTimeInterval
from .hkbTransitionEffect import hkbTransitionEffect
from .hkbCondition import hkbCondition


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbStateMachineTransitionInfo(hk):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1205694735
    __version = 1
    __real_name = "hkbStateMachine::TransitionInfo"

    local_members = (
        Member(0, "triggerInterval", hkbStateMachineTimeInterval),
        Member(16, "initiateInterval", hkbStateMachineTimeInterval),
        Member(32, "transition", hkRefPtr(hkbTransitionEffect, hsh=179771273)),
        Member(40, "condition", hkRefPtr(hkbCondition)),
        Member(48, "eventId", hkInt32),
        Member(52, "toStateId", hkInt32),
        Member(56, "fromNestedStateId", hkInt32),
        Member(60, "toNestedStateId", hkInt32),
        Member(64, "priority", hkInt16),
        Member(66, "flags", hkFlags(hkInt16)),
    )
    members = local_members

    triggerInterval: hkbStateMachineTimeInterval
    initiateInterval: hkbStateMachineTimeInterval
    transition: hkbTransitionEffect
    condition: hkbCondition
    eventId: int
    toStateId: int
    fromNestedStateId: int
    toNestedStateId: int
    priority: int
    flags: hkInt16
