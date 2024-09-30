from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpConvexShape import hkpConvexShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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

    vertexA: Vector4
    vertexB: Vector4
