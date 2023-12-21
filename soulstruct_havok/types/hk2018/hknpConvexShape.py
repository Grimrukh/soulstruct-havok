from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from .core import *
from .hknpShape import hknpShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpConvexShape(hknpShape):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(48, "maxAllowedPenetration", hkHalf16, MemberFlags.Protected),
        Member(50, "vertices", hkRelArray(hkVector4f), MemberFlags.Protected),
    )
    members = hknpShape.members + local_members

    maxAllowedPenetration: float
    vertices: np.ndarray  # `(n, 4)` float32 array
