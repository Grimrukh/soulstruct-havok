from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hknpShape import hknpShape


class hknpConvexShape(hknpShape):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(48, "vertices", hkRelArray(hkVector4)),
    )
    members = hknpShape.members + local_members

    vertices: list[hkVector4]
