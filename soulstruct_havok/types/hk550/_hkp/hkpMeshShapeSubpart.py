from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpMeshShapeIndexStridingType import hkpMeshShapeIndexStridingType
from .hkpMeshShapeMaterialIndexStridingType import hkpMeshShapeMaterialIndexStridingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpMeshShapeSubpart(hk):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpMeshShape::Subpart"

    local_members = (
        Member(0, "vertexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(4, "vertexStriding", _int),
        Member(8, "numVertices", _int),
        Member(12, "indexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(16, "stridingType", hkEnum(hkpMeshShapeIndexStridingType, hkInt8)),
        Member(17, "materialIndexStridingType", hkEnum(hkpMeshShapeMaterialIndexStridingType, hkUint8)),
        Member(20, "indexStriding", _int),
        Member(24, "flipAlternateTriangles", _int),
        Member(28, "numTriangles", _int),
        Member(32, "materialIndexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(36, "materialIndexStriding", hkUint16),
        Member(40, "materialBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(44, "materialStriding", _int),
        Member(48, "numMaterials", hkUint16),
        Member(52, "triangleOffset", _int),
    )
    members = local_members

    vertexBase: None = None
    vertexStriding: int
    numVertices: int
    indexBase: None = None
    stridingType: int
    materialIndexStridingType: int
    indexStriding: int
    flipAlternateTriangles: int  # 0 or 1
    numTriangles: int
    materialIndexBase: None = None
    materialIndexStriding: int
    materialBase: None = None
    materialStriding: int
    numMaterials: int
    triangleOffset: int = -1
