from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpMaterialResponseType import hkpMaterialResponseType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpMaterial(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "responseType", hkEnum(hkpMaterialResponseType, hkInt8)),
        Member(2, "rollingFrictionMultiplier", hkHalf16),
        Member(4, "friction", hkReal),
        Member(8, "restitution", hkReal),
    )
    members = local_members

    responseType: int
    rollingFrictionMultiplier: hkHalf16
    friction: float
    restitution: float
