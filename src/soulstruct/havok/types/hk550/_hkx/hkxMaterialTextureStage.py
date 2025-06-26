from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMaterialTextureStage(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3766860447

    local_members = (
        Member(0, "texture", Ptr(hkReferencedObject)),  # `hkVariant.m_class`
        Member(4, "usageHint", hkInt32),  # NOTE: Could be a `hkxMaterial::TextureType` but not necessarily
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: int
