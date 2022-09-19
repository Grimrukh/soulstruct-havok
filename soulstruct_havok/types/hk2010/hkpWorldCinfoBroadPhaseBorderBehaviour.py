from __future__ import annotations

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *


class hkpWorldCinfoBroadPhaseBorderBehaviour(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkpWorldCinfo::BroadPhaseBorderBehaviour"
    local_members = ()
