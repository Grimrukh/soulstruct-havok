from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


class hkGeometryTriangle(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkGeometry::Triangle"

    local_members = (
        Member(0, "a", _int),
        Member(4, "b", _int),
        Member(8, "c", _int),
        Member(12, "material", _int),
    )
    members = local_members

    a: int
    b: int
    c: int
    material: int
