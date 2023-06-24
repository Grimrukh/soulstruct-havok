from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkaAnimation import hkaAnimation
from .hkaAnimationBindingBlendHint import hkaAnimationBindingBlendHint


@dataclass(slots=True, eq=False, repr=False)
class hkaAnimationBinding(hkReferencedObject):
    alignment = 8
    byte_size = 88
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1548920428
    __version = 3

    local_members = (
        Member(16, "originalSkeletonName", hkStringPtr),
        Member(24, "animation", hkRefPtr(hkaAnimation, hsh=835592334)),
        Member(32, "transformTrackToBoneIndices", hkArray(hkInt16, hsh=2354433887)),
        Member(48, "floatTrackToFloatSlotIndices", hkArray(hkInt16, hsh=2354433887)),
        Member(64, "partitionIndices", hkArray(hkInt16, hsh=2354433887)),
        Member(80, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    animation: hkaAnimation
    transformTrackToBoneIndices: list[int]
    floatTrackToFloatSlotIndices: list[int]
    partitionIndices: list[int]
    blendHint: hkaAnimationBindingBlendHint
