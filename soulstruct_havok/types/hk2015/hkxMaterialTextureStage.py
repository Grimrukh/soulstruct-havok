from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkxMaterialTextureType import hkxMaterialTextureType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMaterialTextureStage(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkxMaterial::TextureStage"

    local_members = (
        Member(0, "texture", hkRefVariant(hkReferencedObject, hsh=2872857893)),
        Member(8, "usageHint", hkEnum(hkxMaterialTextureType, hkInt32)),
        Member(12, "tcoordChannel", hkInt32),
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: hkxMaterialTextureType
    tcoordChannel: int
