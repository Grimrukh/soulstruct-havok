from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from .core import *

from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaDefaultAnimatedReferenceFrame(hkaAnimatedReferenceFrame):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 823768304

    local_members = (
        Member(16, "up", hkVector4),
        Member(32, "forward", hkVector4),
        Member(48, "duration", hkReal),
        Member(52, "referenceFrameSamples", hkArray(hkVector4)),
    )
    members = hkaAnimatedReferenceFrame.members + local_members

    up: Vector4
    forward: Vector4
    duration: float
    referenceFrameSamples: np.ndarray  # `(n, 4)` float32 array
