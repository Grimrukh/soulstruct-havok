from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpConvexShape import hkpConvexShape


class hkpCapsuleShape(hkpConvexShape):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 276111070

    local_members = (
        Member(48, "vertexA", hkVector4, MemberFlags.Protected),
        Member(64, "vertexB", hkVector4, MemberFlags.Protected),
    )
    members = hkpConvexShape.members + local_members

    vertexA: hkVector4
    vertexB: hkVector4
