from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkaAnimation import hkaAnimation
from .hkaAnimationBindingBlendHint import hkaAnimationBindingBlendHint


class hkaAnimationBinding(hkReferencedObject):
    alignment = 16
    byte_size = 88
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(16, "originalSkeletonName", hkStringPtr),
        Member(24, "animation", Ptr(hkaAnimation)),
        Member(32, "transformTrackToBoneIndices", hkArray(hkInt16)),
        Member(48, "floatTrackToFloatSlotIndices", hkArray(hkInt16)),
        Member(64, "partitionIndices", hkArray(hkInt16)),
        Member(80, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    animation: hkaAnimation
    transformTrackToBoneIndices: list[int]
    floatTrackToFloatSlotIndices: list[int]
    partitionIndices: list[int]
    blendHint: int
