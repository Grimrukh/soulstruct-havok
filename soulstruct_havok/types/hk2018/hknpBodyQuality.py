from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *




from .hknpMotionRangeBreachPolicyEnum import hknpMotionRangeBreachPolicyEnum


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpBodyQuality(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4

    local_members = (
        Member(20, "priority", _int),
        Member(24, "supportedFlags", hkFlags(hkUint32)),
        Member(28, "requestedFlags", hkFlags(hkUint32)),
        Member(32, "contactCachingRelativeMovementThreshold", hkReal),
        Member(36, "motionRangeBreachPolicy", hknpMotionRangeBreachPolicyEnum),
        Member(40, "motionWeldBreachPolicy", hknpMotionRangeBreachPolicyEnum),
    )
    members = hkReferencedObject.members + local_members

    priority: int
    supportedFlags: hkUint32
    requestedFlags: hkUint32
    contactCachingRelativeMovementThreshold: float
    motionRangeBreachPolicy: int
    motionWeldBreachPolicy: int
