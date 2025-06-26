from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaSkeletalAnimation import hkaSkeletalAnimation


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSplineSkeletalAnimation(hkaSkeletalAnimation):
    alignment = 4
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    # TODO: hsh unknown

    local_members = (
        Member(36, "numFrames", _int),
        Member(40, "numBlocks", _int),
        Member(44, "maxFramesPerBlock", _int),
        Member(48, "maskAndQuantizationSize", _int),
        Member(52, "blockDuration", hkReal),
        Member(56, "blockInverseDuration", hkReal),
        Member(60, "frameDuration", hkReal),
        Member(64, "blockOffsets", hkArray(hkUint32)),
        Member(76, "floatBlockOffsets", hkArray(hkUint32)),
        Member(88, "transformOffsets", hkArray(hkUint32)),
        Member(100, "floatOffsets", hkArray(hkUint32)),
        Member(112, "data", hkArray(hkUint8)),
        Member(124, "endian", _int),
    )
    members = hkaSkeletalAnimation.members + local_members

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
