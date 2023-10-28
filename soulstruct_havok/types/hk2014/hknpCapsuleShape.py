from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hknpConvexPolytopeShape import hknpConvexPolytopeShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpCapsuleShape(hknpConvexPolytopeShape):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1621581644

    local_members = (
        Member(64, "a", hkVector4),
        Member(80, "b", hkVector4),
    )
    members = hknpConvexPolytopeShape.members + local_members

    a: Vector4
    b: Vector4
