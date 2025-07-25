from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclVirtualCollisionPointsDataEdgeFanSection(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::EdgeFanSection"

    local_members = (
        Member(0, "oppositeRealParticleIndex", hkUint16),
        Member(2, "barycentricDictionaryIndex", hkUint16),
    )
    members = local_members

    oppositeRealParticleIndex: int
    barycentricDictionaryIndex: int
