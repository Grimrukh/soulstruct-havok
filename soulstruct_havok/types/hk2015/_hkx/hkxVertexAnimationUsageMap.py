from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxVertexDescriptionDataUsage import hkxVertexDescriptionDataUsage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxVertexAnimationUsageMap(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkxVertexAnimation::UsageMap"

    local_members = (
        Member(0, "use", hkEnum(hkxVertexDescriptionDataUsage, hkUint16)),
        Member(2, "useIndexOrig", hkUint8),
        Member(3, "useIndexLocal", hkUint8),
    )
    members = local_members

    use: hkxVertexDescriptionDataUsage
    useIndexOrig: int
    useIndexLocal: int
