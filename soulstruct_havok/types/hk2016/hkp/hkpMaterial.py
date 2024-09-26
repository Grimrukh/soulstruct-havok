from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpMaterialResponseType import hkpMaterialResponseType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpMaterial(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(0, "responseType", hkEnum(hkpMaterialResponseType, hkInt8), MemberFlags.Private),
        Member(2, "rollingFrictionMultiplier", hkHalf16, MemberFlags.Private),
        Member(4, "friction", hkReal, MemberFlags.Private),
        Member(8, "restitution", hkReal, MemberFlags.Private),
    )
    members = local_members

    responseType: hkpMaterialResponseType
    rollingFrictionMultiplier: float
    friction: float
    restitution: float
