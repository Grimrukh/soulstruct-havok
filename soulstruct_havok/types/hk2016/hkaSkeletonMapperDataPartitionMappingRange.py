from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeletonMapperDataPartitionMappingRange(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkaSkeletonMapperData::PartitionMappingRange"

    local_members = (
        Member(0, "startMappingIndex", _int),
        Member(4, "numMappings", _int),
    )
    members = local_members

    startMappingIndex: int
    numMappings: int
