from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hknpConvexPolytopeShapeFace(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "firstIndex", hkUint16),
        Member(2, "numIndices", hkUint8),
        Member(3, "minHalfAngle", hkUint8),
    )
    members = local_members

    firstIndex: int
    numIndices: int
    minHalfAngle: int
