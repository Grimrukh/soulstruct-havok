from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpShapeCollection import hkpShapeCollection
from .hkpExtendedMeshShapeTrianglesSubpart import hkpExtendedMeshShapeTrianglesSubpart
from .hkpExtendedMeshShapeShapesSubpart import hkpExtendedMeshShapeShapesSubpart
from .hkpWeldingUtilityWeldingType import hkpWeldingUtilityWeldingType


class hkpExtendedMeshShape(hkpShapeCollection):
    alignment = 16
    byte_size = 320
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4

    local_members = (
        Member(48, "embeddedTrianglesSubpart", hkpExtendedMeshShapeTrianglesSubpart, MemberFlags.Protected),
        Member(192, "aabbHalfExtents", hkVector4),
        Member(208, "aabbCenter", hkVector4),
        Member(224, "materialClass", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(232, "numBitsForSubpartIndex", hkInt32),
        Member(
            240,
            "trianglesSubparts",
            hkArray(hkpExtendedMeshShapeTrianglesSubpart, hsh=1214306214),
            MemberFlags.Protected,
        ),
        Member(256, "shapesSubparts", hkArray(hkpExtendedMeshShapeShapesSubpart), MemberFlags.Protected),
        Member(272, "weldingInfo", hkArray(hkUint16, hsh=3551656838)),
        Member(288, "weldingType", hkEnum(hkpWeldingUtilityWeldingType, hkUint8)),
        Member(292, "defaultCollisionFilterInfo", hkUint32),
        Member(296, "cachedNumChildShapes", hkInt32),
        Member(300, "triangleRadius", hkReal, MemberFlags.Protected),
        Member(304, "padding", hkInt32, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = hkpShapeCollection.members + local_members

    embeddedTrianglesSubpart: hkpExtendedMeshShapeTrianglesSubpart
    aabbHalfExtents: Vector4
    aabbCenter: Vector4
    materialClass: hkReflectDetailOpaque
    numBitsForSubpartIndex: int
    trianglesSubparts: list[hkpExtendedMeshShapeTrianglesSubpart]
    shapesSubparts: list[hkpExtendedMeshShapeShapesSubpart]
    weldingInfo: list[int]
    weldingType: hkpWeldingUtilityWeldingType
    defaultCollisionFilterInfo: int
    cachedNumChildShapes: int
    triangleRadius: float
    padding: int
