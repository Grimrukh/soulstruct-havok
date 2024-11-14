from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxLightLightType(hk):
    """
    POINT_LIGHT = 0
    DIRECTIONAL_LIGHT = 1
    SPOT_LIGHT = 2
    """
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32
    __real_name = "hkxLight::LightType"
    local_members = ()
