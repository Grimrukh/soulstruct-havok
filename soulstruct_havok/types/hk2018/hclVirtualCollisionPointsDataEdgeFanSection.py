from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
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
