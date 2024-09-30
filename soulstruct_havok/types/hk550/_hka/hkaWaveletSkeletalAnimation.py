from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkaSkeletalAnimation import hkaSkeletalAnimation
from .hkaWaveletSkeletalAnimationQuantizationFormat import hkaWaveletSkeletalAnimationQuantizationFormat


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaWaveletSkeletalAnimation(hkaSkeletalAnimation):
    alignment = 16
    byte_size = 92
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(36, "numberOfPoses", hkInt32),
        Member(40, "blockSize", hkInt32),
        Member(44, "qFormat", hkaWaveletSkeletalAnimationQuantizationFormat),
        Member(64, "staticMaskIdx", hkUint32),
        Member(68, "staticDOFsIdx", hkUint32),
        Member(72, "blockIndexIdx", hkUint32),
        Member(76, "blockIndexSize", hkUint32),
        Member(80, "quantizedDataIdx", hkUint32),
        Member(84, "quantizedDataSize", hkUint32),
        Member(88, "dataBuffer", hkArray(hkUint8)),
    )
    members = hkaSkeletalAnimation.members + local_members

    numberOfPoses: int
    blockSize: int
    qFormat: hkaWaveletSkeletalAnimationQuantizationFormat
    staticMaskIdx: int
    staticDOFsIdx: int
    blockIndexIdx: int
    blockIndexSize: int
    quantizedDataIdx: int
    quantizedDataSize: int
    dataBuffer: list[int]
