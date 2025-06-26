from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxAttributeHolder import hkxAttributeHolder
from .hkxMaterialTextureStage import hkxMaterialTextureStage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxTextureInplace(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4132115276

    local_members = (
        Member(0, "fileType", hkStruct(_char, 4)),
        Member(4, "data", SimpleArray(hkUint8)),
    )
    members = local_members

    fileType: tuple[int, int, int, int]  # e.g. 'BMP', 'PNG', 'GIF'
    data: list[int]  # raw file data (still compressed, etc.)
