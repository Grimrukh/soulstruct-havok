from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiStreamingSetGraphConnection(hk):
    alignment = 4
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4
    __real_name = "hkaiStreamingSet::GraphConnection"

    local_members = (
        Member(0, "aNodeIndex", _int),
        Member(4, "bNodeIndex", _int),
        Member(8, "aEdgeData", hkUint32),
        Member(12, "bEdgeData", hkUint32),
        Member(16, "aEdgeCost", hkHalf16),
        Member(18, "bEdgeCost", hkHalf16),
    )
    members = local_members

    aNodeIndex: int
    bNodeIndex: int
    aEdgeData: int
    bEdgeData: int
    aEdgeCost: float
    bEdgeCost: float
