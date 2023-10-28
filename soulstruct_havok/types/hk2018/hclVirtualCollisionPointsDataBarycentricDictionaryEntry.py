from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclVirtualCollisionPointsDataBarycentricDictionaryEntry(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::BarycentricDictionaryEntry"

    local_members = (
        Member(0, "startingBarycentricIndex", hkUint16),
        Member(2, "numBarycentrics", hkUint8),
    )
    members = local_members

    startingBarycentricIndex: int
    numBarycentrics: int
