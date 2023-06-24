from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclVirtualCollisionPointsDataBlock(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::Block"

    local_members = (
        Member(0, "safeDisplacementRadius", hkReal),
        Member(4, "startingVCPIndex", hkUint16),
        Member(6, "numVCPs", hkUint8),
    )
    members = local_members

    safeDisplacementRadius: float
    startingVCPIndex: int
    numVCPs: int
