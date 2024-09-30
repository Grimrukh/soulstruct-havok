from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaWaveletSkeletalAnimationCompressionParams(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "quantizationBits", hkUint16),
        Member(2, "blockSize", hkUint16),
        Member(4, "preserve", hkUint16),
        Member(8, "truncProp", hkReal),
        Member(12, "useOldStyleTruncation", hkBool),
        Member(16, "absolutePositionTolerance", hkReal),
        Member(20, "relativePositionTolerance", hkReal),
        Member(24, "rotationTolerance", hkReal),
        Member(28, "scaleTolerance", hkReal),
    )
    members = local_members

    quantizationBits: int
    blockSize: int
    preserve: int
    truncProp: float
    useOldStyleTruncation: bool
    absolutePositionTolerance: float
    relativePositionTolerance: float
    rotationTolerance: float
    scaleTolerance: float
