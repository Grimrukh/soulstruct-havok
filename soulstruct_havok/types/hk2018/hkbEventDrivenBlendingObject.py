from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbBlendCurveUtilsBlendCurve import hkbBlendCurveUtilsBlendCurve
from .hkbEventDrivenBlendingObjectInternalState import hkbEventDrivenBlendingObjectInternalState


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbEventDrivenBlendingObject(hk):
    alignment = 4
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "weight", hkReal),
        Member(4, "fadeInDuration", hkReal),
        Member(8, "fadeOutDuration", hkReal),
        Member(12, "onEventId", hkInt32),
        Member(16, "offEventId", hkInt32),
        Member(20, "onByDefault", hkBool),
        Member(21, "forceFullFadeDurations", hkBool),
        Member(22, "fadeInOutCurve", hkEnum(hkbBlendCurveUtilsBlendCurve, hkInt8)),
        Member(24, "internalState", hkbEventDrivenBlendingObjectInternalState, MemberFlags.NotSerializable),
    )
    members = local_members

    weight: float
    fadeInDuration: float
    fadeOutDuration: float
    onEventId: int
    offEventId: int
    onByDefault: bool
    forceFullFadeDurations: bool
    fadeInOutCurve: hkbBlendCurveUtilsBlendCurve
    internalState: hkbEventDrivenBlendingObjectInternalState
