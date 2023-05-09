from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxMaterialTextureStageTextureType import hkxMaterialTextureStageTextureType


@dataclass(slots=True, eq=False, repr=False)
class hkxMaterialTextureStage(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "texture", Ptr(hkReferencedObject)),
        Member(4, "usageHint", hkEnum(hkxMaterialTextureStageTextureType, hkInt32)),
        Member(8, "tcoordChannel", hkInt32),
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: int
    tcoordChannel: int
