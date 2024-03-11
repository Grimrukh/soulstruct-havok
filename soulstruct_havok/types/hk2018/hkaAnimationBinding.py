from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkaAnimation import hkaAnimation

from .hkaAnimationBindingBlendHint import hkaAnimationBindingBlendHint


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimationBinding(hkReferencedObject):
    alignment = 8
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(24, "originalSkeletonName", hkStringPtr),
        Member(32, "animation", hkRefPtr(hkaAnimation)),
        Member(40, "transformTrackToBoneIndices", hkArray(hkInt16, hsh=3571075457)),
        Member(56, "floatTrackToFloatSlotIndices", hkArray(hkInt16, hsh=3571075457)),
        Member(72, "partitionIndices", hkArray(hkInt16, hsh=3571075457)),
        Member(88, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: hkStringPtr
    animation: hkaAnimation
    transformTrackToBoneIndices: list[int]
    floatTrackToFloatSlotIndices: list[int]
    partitionIndices: list[int]
    blendHint: int
