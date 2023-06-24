from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkaAnimation import hkaAnimation
from .hkaAnimationBindingBlendHint import hkaAnimationBindingBlendHint


@dataclass(slots=True, eq=False, repr=False)
class hkaAnimationBinding(hkReferencedObject):
    alignment = 16
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "originalSkeletonName", hkStringPtr),
        Member(12, "animation", Ptr(hkaAnimation)),
        Member(16, "transformTrackToBoneIndices", hkArray(hkInt16)),
        Member(28, "floatTrackToFloatSlotIndices", hkArray(hkInt16)),
        Member(40, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    animation: hkaAnimation
    transformTrackToBoneIndices: list[int]
    floatTrackToFloatSlotIndices: list[int]
    blendHint: int
