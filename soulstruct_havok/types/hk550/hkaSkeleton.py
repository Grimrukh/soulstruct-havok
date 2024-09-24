from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkaBone import hkaBone
from .hkaSkeletonLocalFrameOnBone import hkaSkeletonLocalFrameOnBone


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeleton(hkReferencedObject):
    alignment = 16
    byte_size = 84
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 913211936

    local_members = (
        Member(8, "name", hkStringPtr),
        Member(12, "parentIndices", hkArray(hkInt16)),
        Member(24, "bones", hkArray(hkaBone)),
        Member(36, "referencePose", hkArray(hkQsTransform)),
        Member(48, "referenceFloats", hkArray(hkReal)),
        Member(60, "floatSlots", hkArray(hkStringPtr)),
        Member(72, "localFrames", hkArray(hkaSkeletonLocalFrameOnBone)),
    )
    members = hkReferencedObject.members + local_members

    name: str
    parentIndices: list[int]
    bones: list[hkaBone]
    referencePose: list[hkQsTransform]
    referenceFloats: list[float]
    floatSlots: list[str]
    localFrames: list[hkaSkeletonLocalFrameOnBone]
