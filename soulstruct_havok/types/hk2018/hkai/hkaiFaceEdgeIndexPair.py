from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkaiIndex import hkaiIndex


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiFaceEdgeIndexPair(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "faceIndex", hkaiIndex),
        Member(4, "edgeIndex", hkaiIndex),
    )
    members = local_members

    faceIndex: int
    edgeIndex: int
