from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *




class hknpConvexPolytopeShapeFace(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3937242244
    __real_name = "hknpConvexPolytopeShape::Face"

    local_members = (
        Member(0, "firstIndex", hkUint16),
        Member(2, "numIndices", hkUint8),
        Member(3, "minHalfAngle", hkUint8),
    )
    members = local_members

    firstIndex: int
    numIndices: int
    minHalfAngle: int
