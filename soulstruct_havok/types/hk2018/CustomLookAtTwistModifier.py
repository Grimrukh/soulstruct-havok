from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbModifier import hkbModifier
from .CustomLookAtTwistModifierMultiRotationAxisType import CustomLookAtTwistModifierMultiRotationAxisType
from .CustomLookAtTwistModifierTwistParam import CustomLookAtTwistModifierTwistParam
from .CustomLookAtTwistModifierSetAngleMethod import CustomLookAtTwistModifierSetAngleMethod


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class CustomLookAtTwistModifier(hkbModifier):
    alignment = 8
    byte_size = 208
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2219889801
    __version = 1

    local_members = (
        Member(104, "ModifierID", hkInt32),
        Member(108, "rotationAxisType", hkEnum(CustomLookAtTwistModifierMultiRotationAxisType, hkInt8)),
        Member(112, "SensingDummyPoly", hkInt32),
        Member(120, "twistParam", hkArray(CustomLookAtTwistModifierTwistParam, hsh=1928398495)),
        Member(136, "UpLimitAngle", hkReal),
        Member(140, "DownLimitAngle", hkReal),
        Member(144, "RightLimitAngle", hkReal),
        Member(148, "LeftLimitAngle", hkReal),
        Member(152, "UpMinimumAngle", hkReal),
        Member(156, "DownMinimumAngle", hkReal),
        Member(160, "RightMinimumAngle", hkReal),
        Member(164, "LeftMinimumAngle", hkReal),
        Member(168, "SensingAngle", hkInt16),
        Member(170, "setAngleMethod", hkEnum(CustomLookAtTwistModifierSetAngleMethod, hkInt8)),
        Member(171, "isAdditive", hkBool),
        Member(
            176,
            "twistModifierXArray",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            192,
            "twistModifierYArray",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
    )
    members = hkbModifier.members + local_members

    ModifierID: int
    rotationAxisType: CustomLookAtTwistModifierMultiRotationAxisType
    SensingDummyPoly: int
    twistParam: list[CustomLookAtTwistModifierTwistParam]
    UpLimitAngle: float
    DownLimitAngle: float
    RightLimitAngle: float
    LeftLimitAngle: float
    UpMinimumAngle: float
    DownMinimumAngle: float
    RightMinimumAngle: float
    LeftMinimumAngle: float
    SensingAngle: int
    setAngleMethod: CustomLookAtTwistModifierSetAngleMethod
    isAdditive: bool
    twistModifierXArray: list[hkReflectDetailOpaque]
    twistModifierYArray: list[hkReflectDetailOpaque]
