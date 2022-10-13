from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpConvexShape import hkpConvexShape


class hkpBoxShape(hkpConvexShape):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2601362417

    local_members = (
        Member(48, "halfExtents", hkVector4, MemberFlags.Protected),
    )
    members = hkpConvexShape.members + local_members

    halfExtents: Vector4
