from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *




class hclVirtualCollisionPointsDataEdgeFan(hk):
    alignment = 2
    byte_size = 6
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::EdgeFan"

    local_members = (
        Member(0, "realParticleIndex", hkUint16),
        Member(2, "edgeStartIndex", hkUint16),
        Member(4, "numEdges", hkUint8),
    )
    members = local_members

    realParticleIndex: int
    edgeStartIndex: int
    numEdges: int