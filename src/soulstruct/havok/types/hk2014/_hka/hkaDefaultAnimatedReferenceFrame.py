from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from soulstruct.havok.enums import *
from ..core import *

from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaDefaultAnimatedReferenceFrame(hkaAnimatedReferenceFrame):
    alignment = 16
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2816999057

    local_members = (
        Member(20, "up", hkVector4),
        Member(36, "forward", hkVector4),
        Member(52, "duration", hkReal),
        Member(56, "referenceFrameSamples", hkArray(hkVector4, hsh=2234779563)),
    )
    members = hkaAnimatedReferenceFrame.members + local_members

    up: Vector4
    forward: Vector4
    duration: float
    referenceFrameSamples: np.ndarray  # `(n, 4)` float32 array
