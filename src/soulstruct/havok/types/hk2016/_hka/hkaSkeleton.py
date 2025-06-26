from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaBone import hkaBone
from .hkaSkeletonLocalFrameOnBone import hkaSkeletonLocalFrameOnBone
from .hkaSkeletonPartition import hkaSkeletonPartition


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeleton(hkReferencedObject):
    alignment = 8
    byte_size = 136
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 6

    local_members = (
        Member(16, "name", hkStringPtr),
        Member(24, "parentIndices", hkArray(hkInt16, hsh=2354433887)),
        Member(40, "bones", hkArray(hkaBone)),
        Member(56, "referencePose", hkArray(hkQsTransform)),
        Member(72, "referenceFloats", hkArray(hkReal)),
        Member(88, "floatSlots", hkArray(hkStringPtr)),
        Member(104, "localFrames", hkArray(hkaSkeletonLocalFrameOnBone)),
        Member(120, "partitions", hkArray(hkaSkeletonPartition)),
    )
    members = hkReferencedObject.members + local_members

    name: str
    parentIndices: list[int]
    bones: list[hkaBone]
    referencePose: list[hkQsTransform]
    referenceFloats: list[float]
    floatSlots: list[str]
    localFrames: list[hkaSkeletonLocalFrameOnBone]
    partitions: list[hkaSkeletonPartition]
