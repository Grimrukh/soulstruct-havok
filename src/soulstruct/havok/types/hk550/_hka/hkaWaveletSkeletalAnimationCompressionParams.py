from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaWaveletSkeletalAnimationCompressionParams(hk):
    alignment = 16
    byte_size = 36
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        # Bits used for float quantization
        Member(0, "quantizationBits", hkUint16),
        # Block size
        Member(2, "blockSize", hkUint16),
        # (INTERNAL) Allows exact preservation (full 4-bytes floats) of the first 'n' floats during the quantization
        # process
        Member(4, "preserve", hkUint16),
        # If m_useOldStyleTruncation (deprecated) is set to 'true', this is the fraction of wavelet coefficients
        # discarded (set to zero)
        Member(8, "truncProp", hkReal),
        # Allows backwards compatability (see m_truncProp)
        Member(12, "useOldStyleTruncation", hkBool),
        # TrackAnalysis absolute position tolerance. See the "Compression Overview" section of the Userguide
        Member(16, "absolutePositionTolerance", hkReal),
        # TrackAnalysis relative position tolerance. See the "Compression Overview" section of the Userguide
        Member(20, "relativePositionTolerance", hkReal),
        # TrackAnalysis rotation position tolerance. See the "Compression Overview" section of the Userguide
        Member(24, "rotationTolerance", hkReal),
        # TrackAnalysis scale position tolerance. See the "Compression Overview" section of the Userguide
        Member(28, "scaleTolerance", hkReal),
        # TrackAnalysis float tolerance. See the "Compression Overview" section of the Userguide
        Member(32, "absoluteFloatTolerance", hkReal),
    )
    members = local_members

    quantizationBits: int = 8  # range [2, 16]
    blockSize: int = 65535
    preserve: int = 0  # False
    truncProp: float = 0.1
    useOldStyleTruncation: bool = False
    absolutePositionTolerance: float = 0.0
    relativePositionTolerance: float = 0.01
    rotationTolerance: float = 0.001
    scaleTolerance: float = 0.01
    absoluteFloatTolerance: float = 0.001
