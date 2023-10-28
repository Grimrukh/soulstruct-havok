from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from .core import *

from .hknpConvexShape import hknpConvexShape
from .hknpConvexPolytopeShapeFace import hknpConvexPolytopeShapeFace
from .hknpConvexPolytopeShapeConnectivity import hknpConvexPolytopeShapeConnectivity


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpConvexPolytopeShape(hknpConvexShape):
    alignment = 8
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4

    local_members = (
        Member(54, "planes", hkRelArray(hkVector4), MemberFlags.Protected),
        Member(58, "faces", hkRelArray(hknpConvexPolytopeShapeFace), MemberFlags.Protected),
        Member(62, "indices", hkRelArray(hkUint8), MemberFlags.Protected),
        Member(72, "connectivity", hkRefPtr(hknpConvexPolytopeShapeConnectivity), MemberFlags.Protected),
    )
    members = hknpConvexShape.members + local_members

    planes: np.ndarray  # `(n, 4)` float32 array
    faces: list[hknpConvexPolytopeShapeFace]
    indices: list[int]
    connectivity: hknpConvexPolytopeShapeConnectivity
