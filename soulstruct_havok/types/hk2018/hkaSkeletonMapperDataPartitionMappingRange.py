from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *



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
