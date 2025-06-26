from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpExtendedMeshShapeSubpart import hkpExtendedMeshShapeSubpart
from .hkpExtendedMeshShapeIndexStridingType import hkpExtendedMeshShapeIndexStridingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpExtendedMeshShapeTrianglesSubpart(hkpExtendedMeshShapeSubpart):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpExtendedMeshShape::TrianglesSubpart"

    local_members = (
        Member(16, "numTriangleShapes", _int),
        Member(20, "vertexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(24, "vertexStriding", _int),
        Member(28, "numVertices", _int),
        Member(32, "extrusion", hkVector4f),
        Member(48, "indexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(52, "indexStriding", _int),
        Member(56, "stridingType", hkEnum(hkpExtendedMeshShapeIndexStridingType, hkInt8)),
        Member(57, "flipAlternateTriangles", hkInt8),  # maybe, could go here (0)
        Member(60, "triangleOffset", _int),
    )
    members = hkpExtendedMeshShapeSubpart.members + local_members

    numTriangleShapes: int
    vertexBase: None = None
    vertexStriding: int
    numVertices: int
    extrusion: Vector4
    indexBase: None = None
    indexStriding: int
    stridingType: int
    flipAlternateTriangles: int
    triangleOffset: int
