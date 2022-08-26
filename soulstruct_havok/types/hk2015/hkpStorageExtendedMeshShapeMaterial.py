from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpMeshMaterial import hkpMeshMaterial
from .hkHalf16 import hkHalf16


class hkpStorageExtendedMeshShapeMaterial(hkpMeshMaterial):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpStorageExtendedMeshShape::Material"

    local_members = (
        Member(4, "restitution", hkHalf16),
        Member(6, "friction", hkHalf16),
        Member(8, "userData", hkUlong),
    )
    members = hkpMeshMaterial.members + local_members

    restitution: float
    friction: float
    userData: int
