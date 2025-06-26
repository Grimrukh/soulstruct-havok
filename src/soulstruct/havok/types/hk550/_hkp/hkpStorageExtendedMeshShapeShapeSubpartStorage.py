from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpConvexShape import hkpConvexShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpStorageExtendedMeshShapeShapeSubpartStorage(hkReferencedObject):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpStorageExtendedMeshShape::ShapeSubpartStorage"

    local_members = (
        Member(8, "shapes", hkArray(Ptr(hkpConvexShape))),
        Member(20, "materialIndices", hkArray(hkUint8)),
        Member(32, "materials", hkArray(hkUint32)),
        Member(44, "materialIndices16", hkArray(hkUint16)),
    )
    members = hkReferencedObject.members + local_members

    shapes: list[hkpConvexShape]
    materialIndices: list[int]
    materials: list[int]
    materialIndices16: list[int]
