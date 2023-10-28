from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclSimClothDataCollidablePinchingData(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3233440473
    __version = 1
    __real_name = "hclSimClothData::CollidablePinchingData"

    local_members = (
        Member(0, "pinchDetectionEnabled", hkBool),
        Member(1, "pinchDetectionPriority", hkInt8),
        Member(4, "pinchDetectionRadius", hkReal),
    )
    members = local_members

    pinchDetectionEnabled: bool
    pinchDetectionPriority: int
    pinchDetectionRadius: float
