from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMaterialTextureType(hk):
    """
    TEX_UNKNOWN = 0
    TEX_DIFFUSE = 1
    TEX_REFLECTION = 2
    TEX_BUMP = 3
    TEX_NORMAL = 4
    TEX_DISPLACEMENT = 5
    """
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32
    __real_name = "hkxMaterial::TextureType"
    local_members = ()
