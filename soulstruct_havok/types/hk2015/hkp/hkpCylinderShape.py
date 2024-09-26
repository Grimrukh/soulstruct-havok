from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hkpConvexShape import hkpConvexShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpCylinderShape(hkpConvexShape):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2273258696

    local_members = (
        Member(40, "cylRadius", hkReal, MemberFlags.Protected),
        Member(44, "cylBaseRadiusFactorForHeightFieldCollisions", hkReal, MemberFlags.Protected),
        Member(48, "vertexA", hkVector4, MemberFlags.Protected),
        Member(64, "vertexB", hkVector4, MemberFlags.Protected),
        Member(80, "perpendicular1", hkVector4, MemberFlags.Protected),
        Member(96, "perpendicular2", hkVector4, MemberFlags.Protected),
    )
    members = hkpConvexShape.members + local_members

    cylRadius: float
    cylBaseRadiusFactorForHeightFieldCollisions: float
    vertexA: Vector4
    vertexB: Vector4
    perpendicular1: Vector4
    perpendicular2: Vector4
