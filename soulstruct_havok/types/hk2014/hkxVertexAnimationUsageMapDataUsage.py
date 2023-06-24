from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkxVertexAnimationUsageMapDataUsage(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16
    __real_name = "hkxVertexAnimationUsageMap::DataUsage"
    local_members = ()
