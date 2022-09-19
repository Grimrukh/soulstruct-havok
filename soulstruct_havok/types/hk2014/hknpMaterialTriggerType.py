from __future__ import annotations

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *


class hknpMaterialTriggerType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hknpMaterial::TriggerType"
    local_members = ()
