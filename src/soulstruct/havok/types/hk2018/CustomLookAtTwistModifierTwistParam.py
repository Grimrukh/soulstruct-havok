from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .core import *


from .CustomLookAtTwistModifierGainState import CustomLookAtTwistModifierGainState


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class CustomLookAtTwistModifierTwistParam(hk):
    alignment = 4
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1895891218
    __real_name = "CustomLookAtTwistModifier::TwistParam"

    local_members = (
        Member(0, "startBoneIndex", hkInt16),
        Member(2, "endBoneIndex", hkInt16),
        Member(4, "targetRotationRate", hkReal),
        Member(8, "newTargetGain", hkReal),
        Member(12, "onGain", hkReal),
        Member(16, "offGain", hkReal),
        Member(
            20,
            "gainStateX",
            hkEnum(CustomLookAtTwistModifierGainState, hkInt8),
            MemberFlags.NotSerializable,
        ),
        Member(
            21,
            "gainStateY",
            hkEnum(CustomLookAtTwistModifierGainState, hkInt8),
            MemberFlags.NotSerializable,
        ),
    )
    members = local_members

    startBoneIndex: int
    endBoneIndex: int
    targetRotationRate: float
    newTargetGain: float
    onGain: float
    offGain: float
    gainStateX: CustomLookAtTwistModifierGainState
    gainStateY: CustomLookAtTwistModifierGainState
