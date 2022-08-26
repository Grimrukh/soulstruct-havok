from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hknpConvexShape import hknpConvexShape
from .hknpConvexPolytopeShapeFace import hknpConvexPolytopeShapeFace


class hknpConvexPolytopeShape(hknpConvexShape):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(64, "planes", hkRelArray(hkVector4)),
        Member(68, "faces", hkRelArray(hknpConvexPolytopeShapeFace)),
        Member(72, "indices", hkRelArray(hkUint8)),
    )
    members = hknpConvexShape.members + local_members

    planes: list[hkVector4]
    faces: list[hknpConvexPolytopeShapeFace]
    indices: list[int]
