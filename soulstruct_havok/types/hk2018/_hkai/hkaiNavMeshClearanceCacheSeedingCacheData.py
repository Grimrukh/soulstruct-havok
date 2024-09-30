from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkaiNavMeshClearanceCache import hkaiNavMeshClearanceCache


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiNavMeshClearanceCacheSeedingCacheData(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1067411263
    __real_name = "hkaiNavMeshClearanceCacheSeeding::CacheData"

    local_members = (
        Member(0, "id", hkUlong),
        Member(8, "info", hkUint32),
        Member(12, "infoMask", hkUint32),
        Member(16, "initialCache", hkRefPtr(hkaiNavMeshClearanceCache, hsh=1581662512)),
    )
    members = local_members

    id: int
    info: int
    infoMask: int
    initialCache: hkaiNavMeshClearanceCache
