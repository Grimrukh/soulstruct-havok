from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hknpExternMeshShapeGeometry import hknpExternMeshShapeGeometry
from .hkGeometry import hkGeometry


class hknpDefaultExternMeshShapeGeometry(hknpExternMeshShapeGeometry):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "geometry", hkRefPtr(hkGeometry)),
    )
    members = hknpExternMeshShapeGeometry.members + local_members

    geometry: hkGeometry
