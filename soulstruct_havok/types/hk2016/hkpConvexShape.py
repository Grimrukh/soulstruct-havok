from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpSphereRepShape import hkpSphereRepShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpConvexShape(hkpSphereRepShape):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(32, "radius", hkReal, MemberFlags.Protected),
    )
    members = hkpSphereRepShape.members + local_members

    radius: float
