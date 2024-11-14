from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaWaveletSkeletalAnimationQuantizationFormat(hk):
    alignment = 4
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1917482337

    local_members = (
        # Backwards compatibility only - pre-per-track compression.
        Member(0, "maxBitWidth", hkUint8),
        # Always 0 for wavelet since all coefficients are quantized (none preserved).
        Member(1, "preserved", hkUint8),
        # Number of dynamic tracks that are quantized and stored
        Member(4, "numD", hkUint32),
        # Index into the data buffer for the quantization offsets
        Member(8, "offsetIdx", hkUint32),
        # Index into the data buffer for the quantization scales
        Member(12, "scaleIdx", hkUint32),
        # Index into the data buffer for the quantization bidwidths
        Member(16, "bitWidthIdx", hkUint32),
    )
    members = local_members

    maxBitWidth: int
    preserved: int
    numD: int
    offsetIdx: int
    scaleIdx: int
    bitWidthIdx: int
