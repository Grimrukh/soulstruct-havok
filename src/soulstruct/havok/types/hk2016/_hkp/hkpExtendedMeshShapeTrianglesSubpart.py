from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpExtendedMeshShapeSubpart import hkpExtendedMeshShapeSubpart
from .hkpExtendedMeshShapeIndexStridingType import hkpExtendedMeshShapeIndexStridingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpExtendedMeshShapeTrianglesSubpart(hkpExtendedMeshShapeSubpart):
    alignment = 16
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1411582562
    __version = 4
    __real_name = "hkpExtendedMeshShape::TrianglesSubpart"

    local_members = (
        Member(32, "numTriangleShapes", _int),
        Member(40, "vertexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(48, "numVertices", _int),
        Member(56, "indexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(64, "vertexStriding", hkUint16),
        Member(68, "triangleOffset", _int),
        Member(72, "indexStriding", hkUint16),
        Member(74, "stridingType", hkEnum(hkpExtendedMeshShapeIndexStridingType, hkInt8)),
        Member(75, "flipAlternateTriangles", hkInt8),
        Member(80, "extrusion", hkVector4),
        Member(96, "transform", hkQsTransform),
    )
    members = hkpExtendedMeshShapeSubpart.members + local_members

    numTriangleShapes: int
    vertexBase: None = None
    numVertices: int
    indexBase: None = None
    vertexStriding: int
    triangleOffset: int
    indexStriding: int
    stridingType: hkpExtendedMeshShapeIndexStridingType | int
    flipAlternateTriangles: int
    extrusion: Vector4
    transform: hkQsTransform
