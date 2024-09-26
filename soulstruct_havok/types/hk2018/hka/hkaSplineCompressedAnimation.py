from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hkaAnimation import hkaAnimation


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSplineCompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 184
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3521756134

    local_members = (
        Member(64, "numFrames", _int, MemberFlags.Private),
        Member(68, "numBlocks", _int, MemberFlags.Private),
        Member(72, "maxFramesPerBlock", _int, MemberFlags.Private),
        Member(76, "maskAndQuantizationSize", _int, MemberFlags.Private),
        Member(80, "blockDuration", hkReal, MemberFlags.Private),
        Member(84, "blockInverseDuration", hkReal, MemberFlags.Private),
        Member(88, "frameDuration", hkReal, MemberFlags.Private),
        Member(96, "blockOffsets", hkArray(hkUint32, hsh=1109639201), MemberFlags.Private),
        Member(112, "floatBlockOffsets", hkArray(hkUint32, hsh=1109639201), MemberFlags.Private),
        Member(128, "transformOffsets", hkArray(hkUint32, hsh=1109639201), MemberFlags.Private),
        Member(144, "floatOffsets", hkArray(hkUint32, hsh=1109639201), MemberFlags.Private),
        Member(160, "data", hkArray(hkUint8, hsh=2331026425), MemberFlags.Private),
        Member(176, "endian", _int, MemberFlags.Private),
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
