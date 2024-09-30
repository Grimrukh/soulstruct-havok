from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaWaveletSkeletalAnimationQuantizationFormat(hk):
    alignment = 16
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "maxBitWidth", hkUint8),
        Member(1, "preserved", hkUint8),
        Member(4, "numD", hkUint32),
        Member(8, "offsetIdx", hkUint32),
        Member(12, "scaleIdx", hkUint32),
        Member(16, "bitWidthIdx", hkUint32),
    )
    members = local_members

    maxBitWidth: int
    preserved: int
    numD: int
    offsetIdx: int
    scaleIdx: int
    bitWidthIdx: int
