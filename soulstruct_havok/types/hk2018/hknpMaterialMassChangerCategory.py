from __future__ import annotations

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *


class hknpMaterialMassChangerCategory(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hknpMaterial::MassChangerCategory"
    local_members = ()