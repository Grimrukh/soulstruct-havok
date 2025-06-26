from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkaiIndex import hkaiIndex


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiStreamingSetVolumeConnection(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2
    __real_name = "hkaiStreamingSet::VolumeConnection"

    local_members = (
        Member(0, "aCellIndex", hkaiIndex),
        Member(4, "bCellIndex", hkaiIndex),
    )
    members = local_members

    aCellIndex: int
    bCellIndex: int
