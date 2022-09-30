from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *



class hclVirtualCollisionPointsDataBarycentricPair(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::BarycentricPair"

    local_members = (
        Member(0, "u", hkReal),
        Member(4, "v", hkReal),
    )
    members = local_members

    u: float
    v: float