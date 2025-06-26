from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaAnimation import hkaAnimation


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSplineCompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 136
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2833120502

    local_members = (
        Member(40, "numFrames", _int, MemberFlags.Private),
        Member(44, "numBlocks", _int, MemberFlags.Private),
        Member(48, "maxFramesPerBlock", _int, MemberFlags.Private),
        Member(52, "maskAndQuantizationSize", _int, MemberFlags.Private),
        Member(56, "blockDuration", hkReal, MemberFlags.Private),
        Member(60, "blockInverseDuration", hkReal, MemberFlags.Private),
        Member(64, "frameDuration", hkReal, MemberFlags.Private),
        Member(68, "blockOffsets", hkArray(hkUint32), MemberFlags.Private),
        Member(80, "floatBlockOffsets", hkArray(hkUint32), MemberFlags.Private),
        Member(92, "transformOffsets", hkArray(hkUint32), MemberFlags.Private),
        Member(104, "floatOffsets", hkArray(hkUint32), MemberFlags.Private),
        Member(116, "data", hkArray(hkUint8), MemberFlags.Private),
        Member(128, "endian", _int, MemberFlags.Private),
    )
    members = hkaAnimation.members + local_members

    numFrames: int
    numBlocks: int
    maxFramesPerBlock: int
    maskAndQuantizationSize: int
    blockDuration: float
    blockInverseDuration: float
    frameDuration: float
    blockOffsets: list[int]
    floatBlockOffsets: list[int]
    transformOffsets: list[int]
    floatOffsets: list[int]
    data: list[int]
    endian: int
