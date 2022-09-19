from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hclShape import hclShape




class hclTaperedCapsuleShape(hclShape):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3051345063
    __version = 2

    local_members = (
        Member(32, "small", hkVector4, MemberFlags.Protected),
        Member(48, "big", hkVector4, MemberFlags.Protected),
        Member(64, "coneApex", hkVector4, MemberFlags.Protected),
        Member(80, "coneAxis", hkVector4, MemberFlags.Protected),
        Member(96, "lVec", hkVector4, MemberFlags.Protected),
        Member(112, "dVec", hkVector4, MemberFlags.Protected),
        Member(128, "tanThetaVecNeg", hkVector4, MemberFlags.Protected),
        Member(144, "smallRadius", hkReal, MemberFlags.Protected),
        Member(148, "bigRadius", hkReal, MemberFlags.Protected),
        Member(152, "l", hkReal, MemberFlags.Protected),
        Member(156, "d", hkReal, MemberFlags.Protected),
        Member(160, "cosTheta", hkReal, MemberFlags.Protected),
        Member(164, "sinTheta", hkReal, MemberFlags.Protected),
        Member(168, "tanTheta", hkReal, MemberFlags.Protected),
        Member(172, "tanThetaSqr", hkReal, MemberFlags.Protected),
    )
    members = hclShape.members + local_members

    small: Vector4
    big: Vector4
    coneApex: Vector4
    coneAxis: Vector4
    lVec: Vector4
    dVec: Vector4
    tanThetaVecNeg: Vector4
    smallRadius: float
    bigRadius: float
    l: float
    d: float
    cosTheta: float
    sinTheta: float
    tanTheta: float
    tanThetaSqr: float
