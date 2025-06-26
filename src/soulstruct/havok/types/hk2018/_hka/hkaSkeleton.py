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
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1663626346
    __version = 6

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "parentIndices", hkArray(hkInt16, hsh=3571075457)),
        Member(48, "bones", hkArray(hkaBone, hsh=2644325209)),
        Member(64, "referencePose", hkArray(hkQsTransform, hsh=2077323384)),
        Member(80, "referenceFloats", hkArray(hkReal)),
        Member(96, "floatSlots", hkArray(hkStringPtr)),
        Member(112, "localFrames", hkArray(hkaSkeletonLocalFrameOnBone)),
        Member(128, "partitions", hkArray(hkaSkeletonPartition)),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    parentIndices: list[int]
    bones: list[hkaBone]
    referencePose: list[hkQsTransform]
    referenceFloats: list[float]
    floatSlots: list[hkStringPtr]
    localFrames: list[hkaSkeletonLocalFrameOnBone]
    partitions: list[hkaSkeletonPartition]
