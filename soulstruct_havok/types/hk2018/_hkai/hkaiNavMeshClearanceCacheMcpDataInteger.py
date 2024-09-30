from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiNavMeshClearanceCacheMcpDataInteger(hk):
    alignment = 1
    byte_size = 2
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2014773605
    __real_name = "hkaiNavMeshClearanceCache::McpDataInteger"

    local_members = (
        Member(0, "interpolant", hkUint8),
        Member(1, "clearance", hkUint8),
    )
    members = local_members

    interpolant: int
    clearance: int
