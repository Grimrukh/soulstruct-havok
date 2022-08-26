from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpConvexShape import hkpConvexShape


class hkpCapsuleShape(hkpConvexShape):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3708493779

    local_members = (
        Member(32, "vertexA", hkVector4),
        Member(48, "vertexB", hkVector4),
    )
    members = hkpConvexShape.members + local_members

    vertexA: Vector4
    vertexB: Vector4
