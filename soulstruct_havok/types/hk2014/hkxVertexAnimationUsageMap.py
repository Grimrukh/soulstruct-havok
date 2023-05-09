from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxVertexAnimationUsageMapDataUsage import hkxVertexAnimationUsageMapDataUsage


@dataclass(slots=True, eq=False, repr=False)
class hkxVertexAnimationUsageMap(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "use", hkEnum(hkxVertexAnimationUsageMapDataUsage, hkUint16)),
        Member(2, "useIndexOrig", hkUint8),
        Member(3, "useIndexLocal", hkUint8),
    )
    members = local_members

    use: int
    useIndexOrig: int
    useIndexLocal: int
