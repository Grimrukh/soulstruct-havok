from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hknpConvexShape import hknpConvexShape
from .hknpConvexPolytopeShapeFace import hknpConvexPolytopeShapeFace


@dataclass(slots=True, eq=False, repr=False)
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

    planes: list[Vector4]
    faces: list[hknpConvexPolytopeShapeFace]
    indices: list[int]
