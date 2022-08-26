from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkxMaterialTextureStageTextureType import hkxMaterialTextureStageTextureType


class hkxMaterialTextureStage(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "texture", Ptr(hkReferencedObject)),
        Member(8, "usageHint", hkEnum(hkxMaterialTextureStageTextureType, hkInt32)),
        Member(12, "tcoordChannel", hkInt32),
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: int
    tcoordChannel: int
