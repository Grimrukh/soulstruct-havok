from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbEventDrivenBlendingObjectInternalStateFadingState import hkbEventDrivenBlendingObjectInternalStateFadingState


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbEventDrivenBlendingObjectInternalState(hk):
    alignment = 4
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkbEventDrivenBlendingObject::InternalState"

    local_members = (
        Member(0, "weight", hkReal),
        Member(4, "timeElapsed", hkReal),
        Member(8, "onFraction", hkReal),
        Member(12, "onFractionOffset", hkReal),
        Member(16, "fadingState", hkEnum(hkbEventDrivenBlendingObjectInternalStateFadingState, hkInt8)),
    )
    members = local_members

    weight: float
    timeElapsed: float
    onFraction: float
    onFractionOffset: float
    fadingState: hkbEventDrivenBlendingObjectInternalStateFadingState
