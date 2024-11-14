from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxLightLightType import hkxLightLightType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxLight(hk):
    alignment = 16
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2391976339

    local_members = (
        Member(0, "type", hkEnum(hkxLightLightType, hkInt8)),
        Member(16, "position", hkVector4),
        Member(32, "direction", hkVector4),
        Member(48, "color", hkUint32),
        Member(52, "angle", hkReal),
    )
    members = local_members

    type: int
    position: Vector4
    direction: Vector4
    color: int
    angle: float
