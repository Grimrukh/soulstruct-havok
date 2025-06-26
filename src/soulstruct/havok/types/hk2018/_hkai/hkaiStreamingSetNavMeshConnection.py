from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkaiFaceEdgeIndexPair import hkaiFaceEdgeIndexPair


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiStreamingSetNavMeshConnection(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkaiStreamingSet::NavMeshConnection"

    local_members = (
        Member(0, "aFaceEdgeIndex", hkaiFaceEdgeIndexPair),
        Member(8, "bFaceEdgeIndex", hkaiFaceEdgeIndexPair),
    )
    members = local_members

    aFaceEdgeIndex: hkaiFaceEdgeIndexPair
    bFaceEdgeIndex: hkaiFaceEdgeIndexPair
