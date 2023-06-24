from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkpStorageExtendedMeshShapeMaterial import hkpStorageExtendedMeshShapeMaterial


@dataclass(slots=True, eq=False, repr=False)
class hkpStorageExtendedMeshShapeShapeSubpartStorage(hkReferencedObject):
    alignment = 8
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2
    __real_name = "hkpStorageExtendedMeshShape::ShapeSubpartStorage"

    local_members = (
        Member(16, "materialIndices", hkArray(hkUint8, hsh=2877151166)),
        Member(32, "materials", hkArray(hkpStorageExtendedMeshShapeMaterial)),
        Member(48, "materialIndices16", hkArray(hkUint16, hsh=3551656838)),
    )
    members = hkReferencedObject.members + local_members

    materialIndices: list[int]
    materials: list[hkpStorageExtendedMeshShapeMaterial]
    materialIndices16: list[int]
