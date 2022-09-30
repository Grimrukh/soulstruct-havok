from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *





class hclSimClothDataCollidableTransformMap(hk):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclSimClothData::CollidableTransformMap"

    local_members = (
        Member(0, "transformSetIndex", hkInt32),
        Member(8, "transformIndices", hkArray(hkUint32, hsh=1109639201)),
        Member(24, "offsets", hkArray(hkMatrix4, hsh=3899186074)),
    )
    members = local_members

    transformSetIndex: int
    transformIndices: list[int]
    offsets: list[hkMatrix4]