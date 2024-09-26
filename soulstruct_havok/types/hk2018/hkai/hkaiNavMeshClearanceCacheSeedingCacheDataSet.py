from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkaiNavMeshClearanceCacheSeedingCacheData import hkaiNavMeshClearanceCacheSeedingCacheData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiNavMeshClearanceCacheSeedingCacheDataSet(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 428938626
    __real_name = "hkaiNavMeshClearanceCacheSeeding::CacheDataSet"

    local_members = (
        Member(
            24,
            "cacheDatas",
            hkArray(hkaiNavMeshClearanceCacheSeedingCacheData, hsh=2050683118),
            MemberFlags.Private,
        ),
    )
    members = hkReferencedObject.members + local_members

    cacheDatas: list[hkaiNavMeshClearanceCacheSeedingCacheData]
