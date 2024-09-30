from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from ..core import *

from .hknpConvexShape import hknpConvexShape
from .hknpConvexPolytopeShapeFace import hknpConvexPolytopeShapeFace


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpConvexPolytopeShape(hknpConvexShape):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(44, "planes", hkRelArray(hkVector4)),
        Member(48, "faces", hkRelArray(hknpConvexPolytopeShapeFace)),
        Member(52, "indices", hkRelArray(hkUint8)),
    )
    members = hknpConvexShape.members + local_members

    planes: np.ndarray  # `(n, 4)` float32 array
    faces: list[hknpConvexPolytopeShapeFace]
    indices: list[int]
