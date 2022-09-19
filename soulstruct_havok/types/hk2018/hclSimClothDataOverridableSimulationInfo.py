from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *




class hclSimClothDataOverridableSimulationInfo(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3
    __real_name = "hclSimClothData::OverridableSimulationInfo"

    local_members = (
        Member(0, "gravity", hkVector4),
        Member(16, "globalDampingPerSecond", hkReal),
    )
    members = local_members

    gravity: Vector4
    globalDampingPerSecond: float
