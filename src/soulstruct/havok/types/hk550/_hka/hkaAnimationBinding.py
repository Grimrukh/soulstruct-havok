from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaSkeletalAnimation import hkaSkeletalAnimation
from .hkaAnimationBindingBlendHint import hkaAnimationBindingBlendHint


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimationBinding(hk):
    """NOTE: Not a `hkReferencedObject` in Havok 5.5.0."""
    alignment = 4
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4215890036

    local_members = (
        Member(0, "animation", Ptr(hkaSkeletalAnimation)),
        Member(4, "transformTrackToBoneIndices", SimpleArray(hkInt16)),
        Member(12, "floatTrackToFloatSlotIndices", SimpleArray(hkInt16)),
        Member(20, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8)),
    )
    members = local_members

    animation: hkaSkeletalAnimation
    transformTrackToBoneIndices: list[int]
    floatTrackToFloatSlotIndices: list[int]
    blendHint: int = 0  # NORMAL
