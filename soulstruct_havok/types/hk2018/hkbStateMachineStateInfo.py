from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbBindable import hkbBindable
from .hkbStateListener import hkbStateListener
from .hkbStateMachineEventPropertyArray import hkbStateMachineEventPropertyArray
from .hkbStateMachineTransitionInfoArray import hkbStateMachineTransitionInfoArray
from .hkbGenerator import hkbGenerator


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbStateMachineStateInfo(hkbBindable):
    alignment = 8
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2053983971
    __version = 4
    __real_name = "hkbStateMachine::StateInfo"

    local_members = (
        Member(56, "listeners", hkArray(Ptr(hkbStateListener))),
        Member(72, "enterNotifyEvents", hkRefPtr(hkbStateMachineEventPropertyArray)),
        Member(80, "exitNotifyEvents", hkRefPtr(hkbStateMachineEventPropertyArray)),
        Member(
            88,
            "transitions",
            hkRefPtr(hkbStateMachineTransitionInfoArray, hsh=2291663316),
            MemberFlags.Private,
        ),
        Member(96, "generator", hkRefPtr(hkbGenerator, hsh=1798718120), MemberFlags.Private),
        Member(104, "name", hkStringPtr),
        Member(112, "stateId", _int, MemberFlags.Private),
        Member(116, "probability", hkReal),
        Member(120, "enable", hkBool),
        Member(121, "hasEventlessTransitions", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkbBindable.members + local_members

    listeners: list[hkbStateListener]
    enterNotifyEvents: hkbStateMachineEventPropertyArray
    exitNotifyEvents: hkbStateMachineEventPropertyArray
    transitions: hkbStateMachineTransitionInfoArray
    generator: hkbGenerator
    name: hkStringPtr
    stateId: int
    probability: float
    enable: bool
    hasEventlessTransitions: bool
