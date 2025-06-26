from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpMotionPropertiesFullCastSettings(hk):
    alignment = 4
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hknpMotionProperties::FullCastSettings"

    local_members = (
        Member(0, "minSeparation", hkReal),
        Member(4, "minExtraSeparation", hkReal),
        Member(8, "toiSeparation", hkReal),
        Member(12, "toiExtraSeparation", hkReal),
        Member(16, "toiAccuracy", hkReal),
        Member(20, "relativeSafeDeltaTime", hkReal),
        Member(24, "absoluteSafeDeltaTime", hkReal),
        Member(28, "keepTime", hkReal),
        Member(32, "keepDistance", hkReal),
        Member(36, "maxIterations", _int),
    )
    members = local_members

    minSeparation: float
    minExtraSeparation: float
    toiSeparation: float
    toiExtraSeparation: float
    toiAccuracy: float
    relativeSafeDeltaTime: float
    absoluteSafeDeltaTime: float
    keepTime: float
    keepDistance: float
    maxIterations: int
