from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkaBone import hkaBone
from .hkaSkeletonLocalFrameOnBone import hkaSkeletonLocalFrameOnBone


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeleton(hkReferencedObject):
    alignment = 16
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 860733036

    local_members = (
        Member(8, "name", hkStringPtr),
        Member(12, "parentIndices", SimpleArray(hkInt16)),
        Member(20, "bones", SimpleArray(hkaBone)),
        Member(28, "referencePose", SimpleArray(hkQsTransform)),
        Member(36, "floatSlots", SimpleArray(hkStringPtr)),
    )
    members = hkReferencedObject.members + local_members

    name: str
    parentIndices: list[int]
    bones: list[hkaBone]
    referencePose: list[hkQsTransform]
    floatSlots: list[str]
