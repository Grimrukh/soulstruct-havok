from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclVirtualCollisionPointsDataTriangleFanSection(hk):
    alignment = 2
    byte_size = 6
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::TriangleFanSection"

    local_members = (
        Member(0, "oppositeRealParticleIndices", hkGenericStruct(hkUint16, 2)),
        Member(4, "barycentricDictionaryIndex", hkUint16),
    )
    members = local_members

    oppositeRealParticleIndices: tuple[hkUint16]
    barycentricDictionaryIndex: int
