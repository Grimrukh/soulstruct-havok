from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkpShapeCollection import hkpShapeCollection
from .hkpExtendedMeshShapeTrianglesSubpart import hkpExtendedMeshShapeTrianglesSubpart
from .hkpExtendedMeshShapeShapesSubpart import hkpExtendedMeshShapeShapesSubpart
from .hkpWeldingUtilityWeldingType import hkpWeldingUtilityWeldingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpExtendedMeshShape(hkpShapeCollection):
    alignment = 16
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4

    local_members = (
        Member(32, "scaling", hkVector4),
        Member(48, "aabbHalfExtents", hkVector4),
        Member(64, "aabbCenter", hkVector4),
        Member(
            80,
            "trianglesSubparts",
            hkArray(hkpExtendedMeshShapeTrianglesSubpart, flags=0, forced_capacity=0),
            MemberFlags.Protected,
        ),
        Member(92, "numTrianglesSubparts", _int, MemberFlags.Protected),
        Member(
            96,
            "shapesSubparts",
            hkArray(hkpExtendedMeshShapeShapesSubpart, flags=0xC0000000),
            MemberFlags.Protected,
        ),
        Member(108, "numShapesSubparts", _int, MemberFlags.Protected),
        # NOTE: "weldingInfo and "weldingType" absent.
        Member(112, "embeddedTrianglesSubpart", hkpExtendedMeshShapeTrianglesSubpart, MemberFlags.Protected),  # 64 b
        Member(176, "triangleRadius", hkReal, MemberFlags.Protected),
        Member(180, "pad16", hkStruct(hkUint32, 3), MemberFlags.NotSerializable | MemberFlags.Protected),
    )

    members = hkpShapeCollection.members + local_members

    scaling: Vector4
    aabbHalfExtents: Vector4
    aabbCenter: Vector4
    trianglesSubparts: list[hkpExtendedMeshShapeTrianglesSubpart]
    numTrianglesSubparts: int
    shapesSubparts: list[hkpExtendedMeshShapeShapesSubpart]
    numShapesSubparts: int
    embeddedTrianglesSubpart: hkpExtendedMeshShapeTrianglesSubpart
    triangleRadius: float
    pad16: tuple[int, ...]
