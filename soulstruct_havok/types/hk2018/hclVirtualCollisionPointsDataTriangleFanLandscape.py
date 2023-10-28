from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclVirtualCollisionPointsDataTriangleFanLandscape(hk):
    alignment = 2
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::TriangleFanLandscape"

    local_members = (
        Member(0, "realParticleIndex", hkUint16),
        Member(2, "triangleStartIndex", hkUint16),
        Member(4, "vcpStartIndex", hkUint16),
        Member(6, "numTriangles", hkUint8),
    )
    members = local_members

    realParticleIndex: int
    triangleStartIndex: int
    vcpStartIndex: int
    numTriangles: int
