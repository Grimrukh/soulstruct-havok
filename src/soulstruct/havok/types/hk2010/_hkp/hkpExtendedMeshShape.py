from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpShapeCollection import hkpShapeCollection
from .hkpExtendedMeshShapeTrianglesSubpart import hkpExtendedMeshShapeTrianglesSubpart
from .hkpExtendedMeshShapeShapesSubpart import hkpExtendedMeshShapeShapesSubpart
from .hkpWeldingUtilityWeldingType import hkpWeldingUtilityWeldingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpExtendedMeshShape(hkpShapeCollection):
    alignment = 16
    byte_size = 240
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4

    # TODO: adjusted, but obviously could have missed something
    local_members = (
        Member(32, "embeddedTrianglesSubpart", hkpExtendedMeshShapeTrianglesSubpart, MemberFlags.Protected),
        Member(144, "aabbHalfExtents", hkVector4),
        Member(160, "aabbCenter", hkVector4),
        Member(176, "materialClass", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(180, "numBitsForSubpartIndex", hkInt32),
        Member(
            184,
            "trianglesSubparts",
            hkArray(hkpExtendedMeshShapeTrianglesSubpart),
            MemberFlags.Protected,
        ),
        Member(196, "shapesSubparts", hkArray(hkpExtendedMeshShapeShapesSubpart), MemberFlags.Protected),
        Member(208, "weldingInfo", hkArray(hkUint16)),
        Member(220, "weldingType", hkEnum(hkpWeldingUtilityWeldingType, hkUint8)),
        Member(224, "defaultCollisionFilterInfo", hkUint32),
        Member(228, "cachedNumChildShapes", hkInt32),
        Member(232, "triangleRadius", hkReal, MemberFlags.Protected),
        Member(236, "padding", hkInt32, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = hkpShapeCollection.members + local_members

    embeddedTrianglesSubpart: hkpExtendedMeshShapeTrianglesSubpart
    aabbHalfExtents: Vector4
    aabbCenter: Vector4
    materialClass: None = None
    numBitsForSubpartIndex: int
    trianglesSubparts: list[hkpExtendedMeshShapeTrianglesSubpart]
    shapesSubparts: list[hkpExtendedMeshShapeShapesSubpart]
    weldingInfo: list[int]
    weldingType: hkpWeldingUtilityWeldingType
    defaultCollisionFilterInfo: int
    cachedNumChildShapes: int
    triangleRadius: float
    padding: int
