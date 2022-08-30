from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkGeometryTriangle import hkGeometryTriangle


class hkGeometry(hkReferencedObject):
    alignment = 4
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "vertices", hkArray(hkVector4)),
        Member(12, "triangles", hkArray(hkGeometryTriangle)),
    )
    members = hkReferencedObject.members + local_members

    vertices: list[hkVector4]
    triangles: list[hkGeometryTriangle]
