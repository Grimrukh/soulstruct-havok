from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkaSkeleton import hkaSkeleton
from .hkaSkeletonMapperDataSimpleMapping import hkaSkeletonMapperDataSimpleMapping
from .hkaSkeletonMapperDataChainMapping import hkaSkeletonMapperDataChainMapping
from .hkaSkeletonMapperDataMappingType import hkaSkeletonMapperDataMappingType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeletonMapperData(hk):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "skeletonA", Ptr(hkaSkeleton)),
        Member(4, "skeletonB", Ptr(hkaSkeleton)),
        Member(8, "simpleMappings", hkArray(hkaSkeletonMapperDataSimpleMapping)),
        Member(20, "chainMappings", hkArray(hkaSkeletonMapperDataChainMapping)),
        Member(32, "unmappedBones", hkArray(hkInt16)),
        Member(48, "extractedMotionMapping", hkQsTransform),
        Member(96, "keepUnmappedLocal", hkBool),
        Member(100, "mappingType", hkEnum(hkaSkeletonMapperDataMappingType, hkInt32)),
    )
    members = local_members

    skeletonA: hkaSkeleton
    skeletonB: hkaSkeleton
    simpleMappings: list[hkaSkeletonMapperDataSimpleMapping]
    chainMappings: list[hkaSkeletonMapperDataChainMapping]
    unmappedBones: list[int]
    extractedMotionMapping: hkQsTransform
    keepUnmappedLocal: bool
    mappingType: int
