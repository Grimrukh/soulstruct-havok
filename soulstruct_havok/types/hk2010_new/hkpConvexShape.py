from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpSphereRepShape import hkpSphereRepShape


class hkpConvexShape(hkpSphereRepShape):
    alignment = 16
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "radius", hkReal),
    )
    members = hkpSphereRepShape.members + local_members

    radius: float
