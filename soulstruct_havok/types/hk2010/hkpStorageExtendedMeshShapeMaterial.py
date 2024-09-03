from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkpMeshMaterial import hkpMeshMaterial


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpStorageExtendedMeshShapeMaterial(hkpMeshMaterial):
    alignment = 8
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpStorageExtendedMeshShape::Material"

    # TODO: adjusted
    local_members = (
        Member(4, "restitution", hkHalf16),
        Member(6, "friction", hkHalf16),
        Member(8, "userData", hkUint32),
    )
    members = hkpMeshMaterial.members + local_members

    restitution: float
    friction: float
    userData: int
