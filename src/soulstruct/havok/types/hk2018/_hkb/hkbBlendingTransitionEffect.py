from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbTransitionEffect import hkbTransitionEffect
from .hkbBlendingTransitionEffectEndMode import hkbBlendingTransitionEffectEndMode
from .hkbBlendCurveUtilsBlendCurve import hkbBlendCurveUtilsBlendCurve
from .hkbTransitionEffectSelfTransitionMode import hkbTransitionEffectSelfTransitionMode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbBlendingTransitionEffect(hkbTransitionEffect):
    alignment = 16
    byte_size = 352
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2162729807
    __version = 2

    local_members = (
        Member(184, "duration", hkReal),
        Member(188, "toGeneratorStartTimeFraction", hkReal),
        Member(192, "flags", hkFlags(hkUint16)),
        Member(194, "endMode", hkEnum(hkbBlendingTransitionEffectEndMode, hkInt8)),
        Member(195, "blendCurve", hkEnum(hkbBlendCurveUtilsBlendCurve, hkInt8)),
        Member(196, "alignmentBone", hkInt16),
        Member(208, "fromPos", hkVector4, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(224, "fromRot", hkQuaternion, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(240, "toPos", hkVector4, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(256, "toRot", hkQuaternion, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(272, "lastPos", hkVector4, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(288, "lastRot", hkQuaternion, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            304,
            "characterPoseAtBeginningOfTransition",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(320, "timeRemaining", hkReal, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(324, "timeInTransition", hkReal, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            328,
            "toGeneratorSelfTranstitionMode",
            hkEnum(hkbTransitionEffectSelfTransitionMode, hkInt8),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(329, "initializeCharacterPose", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(330, "alignThisFrame", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(331, "alignmentFinished", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            336,
            "parentStateMachine",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(344, "toGeneratorIsCurrentState", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = hkbTransitionEffect.members + local_members

    duration: float
    toGeneratorStartTimeFraction: float
    flags: hkUint16
    endMode: hkbBlendingTransitionEffectEndMode
    blendCurve: hkbBlendCurveUtilsBlendCurve
    alignmentBone: int
    fromPos: hkVector4
    fromRot: hkQuaternion
    toPos: hkVector4
    toRot: hkQuaternion
    lastPos: hkVector4
    lastRot: hkQuaternion
    characterPoseAtBeginningOfTransition: list[hkReflectDetailOpaque]
    timeRemaining: float
    timeInTransition: float
    toGeneratorSelfTranstitionMode: hkbTransitionEffectSelfTransitionMode
    initializeCharacterPose: bool
    alignThisFrame: bool
    alignmentFinished: bool
    parentStateMachine: hkReflectDetailOpaque
    toGeneratorIsCurrentState: bool
