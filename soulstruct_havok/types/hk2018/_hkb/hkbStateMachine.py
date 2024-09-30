from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator
from .hkbEvent import hkbEvent
from .hkbCustomIdSelector import hkbCustomIdSelector
from .hkbStateMachineStartStateMode import hkbStateMachineStartStateMode
from .hkbStateMachineStateMachineSelfTransitionMode import hkbStateMachineStateMachineSelfTransitionMode
from .hkbStateMachineStateInfo import hkbStateMachineStateInfo
from .hkbStateMachineTransitionInfoArray import hkbStateMachineTransitionInfoArray


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbStateMachine(hkbGenerator):
    alignment = 8
    byte_size = 352
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2831816277
    __version = 5

    local_members = (
        Member(152, "eventToSendWhenStateOrTransitionChanges", hkbEvent),
        Member(176, "startStateIdSelector", hkRefPtr(hkbCustomIdSelector, hsh=849426879)),
        Member(184, "startStateId", hkInt32),
        Member(188, "returnToPreviousStateEventId", hkInt32),
        Member(192, "randomTransitionEventId", hkInt32),
        Member(196, "transitionToNextHigherStateEventId", hkInt32),
        Member(200, "transitionToNextLowerStateEventId", hkInt32),
        Member(204, "syncVariableIndex", hkInt32),
        Member(208, "currentStateId", hkInt32, MemberFlags.NotSerializable),
        Member(212, "wrapAroundStateId", hkBool),
        Member(213, "maxSimultaneousTransitions", hkInt8),
        Member(214, "startStateMode", hkEnum(hkbStateMachineStartStateMode, hkInt8)),
        Member(215, "selfTransitionMode", hkEnum(hkbStateMachineStateMachineSelfTransitionMode, hkInt8)),
        Member(216, "isActive", hkBool, MemberFlags.NotSerializable),
        Member(
            224,
            "states",
            hkArray(Ptr(hkbStateMachineStateInfo, hsh=1087135968), hsh=1882418398),
            MemberFlags.Private,
        ),
        Member(
            240,
            "wildcardTransitions",
            Ptr(hkbStateMachineTransitionInfoArray, hsh=3164094228),
            MemberFlags.Private,
        ),
        Member(
            248,
            "stateIdToIndexMap",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            256,
            "activeTransitions",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            272,
            "transitionFlags",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            288,
            "wildcardTransitionFlags",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            304,
            "delayedTransitions",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(320, "timeInState", hkReal, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(324, "lastLocalTime", hkReal, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(328, "previousStateId", hkInt32, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            332,
            "nextStartStateIndexOverride",
            hkInt32,
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(336, "stateOrTransitionChanged", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(337, "echoNextUpdate", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            338,
            "hasEventlessWildcardTransitions",
            hkBool,
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            344,
            "eventIdToTransitionInfoIndicesMap",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
    )
    members = hkbGenerator.members + local_members

    eventToSendWhenStateOrTransitionChanges: hkbEvent
    startStateIdSelector: hkbCustomIdSelector
    startStateId: int
    returnToPreviousStateEventId: int
    randomTransitionEventId: int
    transitionToNextHigherStateEventId: int
    transitionToNextLowerStateEventId: int
    syncVariableIndex: int
    currentStateId: int
    wrapAroundStateId: bool
    maxSimultaneousTransitions: int
    startStateMode: hkbStateMachineStartStateMode
    selfTransitionMode: hkbStateMachineStateMachineSelfTransitionMode
    isActive: bool
    states: list[hkbStateMachineStateInfo]
    wildcardTransitions: hkbStateMachineTransitionInfoArray
    stateIdToIndexMap: hkReflectDetailOpaque
    activeTransitions: list[hkReflectDetailOpaque]
    transitionFlags: list[hkReflectDetailOpaque]
    wildcardTransitionFlags: list[hkReflectDetailOpaque]
    delayedTransitions: list[hkReflectDetailOpaque]
    timeInState: float
    lastLocalTime: float
    previousStateId: int
    nextStartStateIndexOverride: int
    stateOrTransitionChanged: bool
    echoNextUpdate: bool
    hasEventlessWildcardTransitions: bool
    eventIdToTransitionInfoIndicesMap: hkReflectDetailOpaque
