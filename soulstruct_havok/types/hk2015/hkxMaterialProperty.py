from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


class hkxMaterialProperty(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkxMaterial::Property"

    local_members = (
        Member(0, "key", hkUint32),
        Member(4, "value", hkUint32),
    )
    members = local_members

    key: int
    value: int