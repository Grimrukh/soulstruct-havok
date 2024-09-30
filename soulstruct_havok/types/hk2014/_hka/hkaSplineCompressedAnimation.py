from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkaAnimation import hkaAnimation


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSplineCompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 469459246

    local_members = (
        Member(56, "numFrames", _int, MemberFlags.Private),
        Member(60, "numBlocks", _int, MemberFlags.Private),
        Member(64, "maxFramesPerBlock", _int, MemberFlags.Private),
        Member(68, "maskAndQuantizationSize", _int, MemberFlags.Private),
        Member(72, "blockDuration", hkReal, MemberFlags.Private),
        Member(76, "blockInverseDuration", hkReal, MemberFlags.Private),
        Member(80, "frameDuration", hkReal, MemberFlags.Private),
        Member(88, "blockOffsets", hkArray(hkUint32, hsh=4255738572), MemberFlags.Private),
        Member(104, "floatBlockOffsets", hkArray(hkUint32, hsh=4255738572), MemberFlags.Private),
        Member(120, "transformOffsets", hkArray(hkUint32, hsh=4255738572), MemberFlags.Private),
        Member(136, "floatOffsets", hkArray(hkUint32, hsh=4255738572), MemberFlags.Private),
        Member(152, "data", hkArray(hkUint8, hsh=2877151166), MemberFlags.Private),
        Member(168, "endian", _int, MemberFlags.Private),
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
