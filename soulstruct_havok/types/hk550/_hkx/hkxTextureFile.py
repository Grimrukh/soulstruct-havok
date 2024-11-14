from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxAttributeHolder import hkxAttributeHolder
from .hkxMaterialTextureStage import hkxMaterialTextureStage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxTextureFile(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 35123063

    local_members = (
        Member(0, "filename", hkStringPtr),
    )
    members = local_members

    filename: str
