from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpShapeCollection import hkpShapeCollection
from .hkpMeshShapeSubpart import hkpMeshShapeSubpart
from .hkpWeldingUtilityWeldingType import hkpWeldingUtilityWeldingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpMeshShape(hkpShapeCollection):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4

    local_members = (
        Member(32, "scaling", hkVector4),
        Member(48, "numBitsForSubpartIndex", hkInt32),
        Member(52, "subparts", hkArray(hkpMeshShapeSubpart, flags=0xC0000000)),  # TODO: forced capacity?
        Member(64, "weldingInfo", hkArray(hkUint16)),
        Member(76, "weldingType", hkEnum(hkpWeldingUtilityWeldingType, hkUint8)),
        Member(80, "radius", hkReal),
        Member(84, "pad", hkStruct(_int, 3)),
    )

    members = hkpShapeCollection.members + local_members

    scaling: Vector4
    numBitsForSubpartIndex: int
    subparts: list[hkpMeshShapeSubpart]
    weldingInfo: int
    weldingType: int = 6  # WELDING_TYPE_NONE
    radius: float
    pad: tuple[int, int, int] = (0, 0, 0)
