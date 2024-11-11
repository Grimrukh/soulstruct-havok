from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *

from ..core import *
from .hkpShapeContainer import hkpShapeContainer
from .hkpSimpleMeshShapeTriangle import hkpSimpleMeshShapeTriangle
from .hkpWeldingUtilityWeldingType import hkpWeldingUtilityWeldingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpSimpleMeshShape(hkpShapeContainer):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    local_members = (
        Member(4, "vertices", hkArray(hkVector4)),
        Member(16, "triangles", hkArray(hkpSimpleMeshShapeTriangle)),
        Member(28, "materialIndices", hkArray(hkUint8)),
        Member(40, "radius", hkReal),
        Member(44, "weldingType", hkEnum(hkpWeldingUtilityWeldingType, hkUint8)),
    )

    members = hkpShapeContainer.members + local_members

    vertices: list[Vector4]
    triangles: list[hkpSimpleMeshShapeTriangle]
    materialIndices: list[int]
    radius: float = 0.05
    weldingType: int = 6  # WELDING_TYPE_NONE
