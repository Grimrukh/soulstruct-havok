from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaSkeleton import hkaSkeleton

from .hkaSkeletonMapperDataPartitionMappingRange import hkaSkeletonMapperDataPartitionMappingRange
from .hkaSkeletonMapperDataSimpleMapping import hkaSkeletonMapperDataSimpleMapping
from .hkaSkeletonMapperDataChainMapping import hkaSkeletonMapperDataChainMapping


from .hkaSkeletonMapperDataMappingType import hkaSkeletonMapperDataMappingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeletonMapperData(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(0, "skeletonA", hkRefPtr(hkaSkeleton, hsh=3659816570)),
        Member(8, "skeletonB", hkRefPtr(hkaSkeleton, hsh=3659816570)),
        Member(16, "partitionMap", hkArray(hkInt16, hsh=3571075457)),
        Member(32, "simpleMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange)),
        Member(48, "chainMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange)),
        Member(64, "simpleMappings", hkArray(hkaSkeletonMapperDataSimpleMapping, hsh=2548487613)),
        Member(80, "chainMappings", hkArray(hkaSkeletonMapperDataChainMapping)),
        Member(96, "unmappedBones", hkArray(hkInt16, hsh=3571075457)),
        Member(112, "extractedMotionMapping", hkQsTransform),
        Member(160, "keepUnmappedLocal", hkBool),
        Member(164, "mappingType", hkEnum(hkaSkeletonMapperDataMappingType, hkInt32)),
    )
    members = local_members

    skeletonA: hkaSkeleton
    skeletonB: hkaSkeleton
    partitionMap: list[int]
    simpleMappingPartitionRanges: list[hkaSkeletonMapperDataPartitionMappingRange]
    chainMappingPartitionRanges: list[hkaSkeletonMapperDataPartitionMappingRange]
    simpleMappings: list[hkaSkeletonMapperDataSimpleMapping]
    chainMappings: list[hkaSkeletonMapperDataChainMapping]
    unmappedBones: list[int]
    extractedMotionMapping: hkQsTransform
    keepUnmappedLocal: bool
    mappingType: int | hkaSkeletonMapperDataMappingType
