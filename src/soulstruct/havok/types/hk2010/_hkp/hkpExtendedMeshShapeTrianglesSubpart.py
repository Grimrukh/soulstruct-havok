from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpExtendedMeshShapeSubpart import hkpExtendedMeshShapeSubpart
from .hkpExtendedMeshShapeIndexStridingType import hkpExtendedMeshShapeIndexStridingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpExtendedMeshShapeTrianglesSubpart(hkpExtendedMeshShapeSubpart):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpExtendedMeshShape::TrianglesSubpart"

    # TODO: CORRECT
    local_members = (
        Member(20, "numTriangleShapes", _int),
        Member(24, "vertexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(28, "numVertices", _int),
        Member(32, "indexBase", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(36, "vertexStriding", hkUint16),
        Member(40, "triangleOffset", _int),
        Member(44, "indexStriding", hkUint16),
        Member(46, "stridingType", hkEnum(hkpExtendedMeshShapeIndexStridingType, hkInt8)),
        Member(47, "flipAlternateTriangles", hkInt8),
        Member(48, "extrusion", hkVector4),
        Member(64, "transform", hkQsTransform),
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
