from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hknpConvexPolytopeShape import hknpConvexPolytopeShape



class hknpCapsuleShape(hknpConvexPolytopeShape):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3934518676

    local_members = (
        Member(80, "a", hkVector4, MemberFlags.Protected),
        Member(96, "b", hkVector4, MemberFlags.Protected),
    )
    members = hknpConvexPolytopeShape.members + local_members

    a: Vector4
    b: Vector4
