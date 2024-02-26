from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbStateMachineTransitionInfo import hkbStateMachineTransitionInfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbStateMachineTransitionInfoArray(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 295541510
    __real_name = "hkbStateMachine::TransitionInfoArray"

    local_members = (
        Member(24, "transitions", hkArray(hkbStateMachineTransitionInfo, hsh=1432063150)),
        Member(40, "hasEventlessTransitions", hkBool, MemberFlags.NotSerializable),
        Member(41, "hasTimeBoundedTransitions", hkBool, MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    transitions: list[hkbStateMachineTransitionInfo]
    hasEventlessTransitions: bool
    hasTimeBoundedTransitions: bool
