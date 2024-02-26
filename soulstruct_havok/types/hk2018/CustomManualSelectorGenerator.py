from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbGenerator import hkbGenerator
from .CustomManualSelectorGeneratorOffsetType import CustomManualSelectorGeneratorOffsetType
from .CustomManualSelectorGeneratorAnimeEndEventType import CustomManualSelectorGeneratorAnimeEndEventType
from .CustomManualSelectorGeneratorChangeTypeOfSelectedIndexAfterActivate import CustomManualSelectorGeneratorChangeTypeOfSelectedIndexAfterActivate
from .hkbTransitionEffect import hkbTransitionEffect
from .CustomManualSelectorGeneratorReplanningAI import CustomManualSelectorGeneratorReplanningAI
from .CustomManualSelectorGeneratorRideSync import CustomManualSelectorGeneratorRideSync
from .hkbEvent import hkbEvent


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class CustomManualSelectorGenerator(hkbGenerator):
    alignment = 8
    byte_size = 280
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3571293576

    local_members = (
        Member(152, "generators", hkArray(Ptr(hkbGenerator, hsh=389751017), hsh=1309078354)),
        Member(168, "offsetType", hkEnum(CustomManualSelectorGeneratorOffsetType, hkInt32)),
        Member(172, "animId", hkInt32),
        Member(176, "animeEndEventType", hkEnum(CustomManualSelectorGeneratorAnimeEndEventType, hkInt32)),
        Member(180, "enableScript", hkBool),
        Member(181, "enableTae", hkBool),
        Member(
            182,
            "changeTypeOfSelectedIndexAfterActivate",
            hkEnum(CustomManualSelectorGeneratorChangeTypeOfSelectedIndexAfterActivate, hkUint8),
        ),
        Member(184, "generatorChangedTransitionEffect", Ptr(hkbTransitionEffect)),
        Member(192, "checkAnimEndSlotNo", hkInt32),
        Member(196, "replanningAI", hkEnum(CustomManualSelectorGeneratorReplanningAI, hkUint8)),
        Member(197, "rideSync", hkEnum(CustomManualSelectorGeneratorRideSync, hkUint8)),
        Member(200, "endEvent", hkbEvent, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(224, "preLocalTime", hkReal, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(228, "localTime", hkReal, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(232, "animeDuration", hkReal, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(236, "argTaeId", hkInt32, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(
            240,
            "scriptGenerator",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(248, "stateId", hkInt32, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(252, "isFirstUpdate", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(253, "isAnimTest", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(254, "isSelfTransition", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(256, "currentGeneratorIndex", hkInt16, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(258, "generatorIndexAtActivate", hkInt16, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            264,
            "activeTransitions",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
    )
    members = hkbGenerator.members + local_members

    generators: list[hkbGenerator]
    offsetType: CustomManualSelectorGeneratorOffsetType
    animId: int
    animeEndEventType: CustomManualSelectorGeneratorAnimeEndEventType
    enableScript: bool
    enableTae: bool
    changeTypeOfSelectedIndexAfterActivate: CustomManualSelectorGeneratorChangeTypeOfSelectedIndexAfterActivate
    generatorChangedTransitionEffect: hkbTransitionEffect
    checkAnimEndSlotNo: int
    replanningAI: CustomManualSelectorGeneratorReplanningAI
    rideSync: CustomManualSelectorGeneratorRideSync
    endEvent: hkbEvent
    preLocalTime: float
    localTime: float
    animeDuration: float
    argTaeId: int
    scriptGenerator: hkReflectDetailOpaque
    stateId: int
    isFirstUpdate: bool
    isAnimTest: bool
    isSelfTransition: bool
    currentGeneratorIndex: int
    generatorIndexAtActivate: int
    activeTransitions: list[hkReflectDetailOpaque]
