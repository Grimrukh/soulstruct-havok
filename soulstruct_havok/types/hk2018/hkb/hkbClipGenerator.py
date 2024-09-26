from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator
from .hkbClipTriggerArray import hkbClipTriggerArray
from .hkbClipGeneratorPlaybackMode import hkbClipGeneratorPlaybackMode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbClipGenerator(hkbGenerator):
    alignment = 16
    byte_size = 352
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1396978635
    __version = 5

    local_members = (
        Member(152, "animationName", hkStringPtr),
        Member(160, "triggers", hkRefPtr(hkbClipTriggerArray)),
        Member(168, "userPartitionMask", hkUint32),
        Member(172, "cropStartAmountLocalTime", hkReal),
        Member(176, "cropEndAmountLocalTime", hkReal),
        Member(180, "startTime", hkReal),
        Member(184, "playbackSpeed", hkReal),
        Member(188, "enforcedDuration", hkReal),
        Member(192, "userControlledTimeFraction", hkReal),
        Member(196, "mode", hkEnum(hkbClipGeneratorPlaybackMode, hkInt8)),
        Member(197, "flags", hkInt8),
        Member(198, "animationInternalId", hkInt16, MemberFlags.Private),
        Member(
            200,
            "animDatas",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            216,
            "animationControl",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            224,
            "originalTriggers",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            232,
            "mapperData",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(240, "binding", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
        Member(248, "numAnimationTracks", hkInt32, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(256, "extractedMotion", hkQsTransform, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            304,
            "echos",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(320, "localTime", hkReal, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(324, "time", hkReal, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            328,
            "previousUserControlledTimeFraction",
            hkReal,
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(332, "bufferSize", hkInt32, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(336, "atEnd", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(337, "ignoreStartTime", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(338, "pingPongBackward", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = hkbGenerator.members + local_members

    animationName: hkStringPtr
    triggers: hkbClipTriggerArray
    userPartitionMask: int
    cropStartAmountLocalTime: float
    cropEndAmountLocalTime: float
    startTime: float
    playbackSpeed: float
    enforcedDuration: float
    userControlledTimeFraction: float
    mode: hkbClipGeneratorPlaybackMode
    flags: int
    animationInternalId: int
    animDatas: list[hkReflectDetailOpaque]
    animationControl: hkReflectDetailOpaque
    originalTriggers: hkReflectDetailOpaque
    mapperData: hkReflectDetailOpaque
    binding: hkReflectDetailOpaque
    numAnimationTracks: int
    extractedMotion: hkQsTransform
    echos: list[hkReflectDetailOpaque]
    localTime: float
    time: float
    previousUserControlledTimeFraction: float
    bufferSize: int
    atEnd: bool
    ignoreStartTime: bool
    pingPongBackward: bool
