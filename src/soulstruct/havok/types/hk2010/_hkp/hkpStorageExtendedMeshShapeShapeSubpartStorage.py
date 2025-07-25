from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpStorageExtendedMeshShapeMaterial import hkpStorageExtendedMeshShapeMaterial


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpStorageExtendedMeshShapeShapeSubpartStorage(hkReferencedObject):
    alignment = 8
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpStorageExtendedMeshShape::ShapeSubpartStorage"

    # TODO: adjusted
    local_members = (
        Member(8, "materialIndices", hkArray(hkUint8, hsh=2877151166)),
        Member(20, "materials", hkArray(hkpStorageExtendedMeshShapeMaterial)),
        Member(32, "materialIndices16", hkArray(hkUint16, hsh=3551656838)),
    )
    members = hkReferencedObject.members + local_members

    materialIndices: list[int]
    materials: list[hkpStorageExtendedMeshShapeMaterial]
    materialIndices16: list[int]
