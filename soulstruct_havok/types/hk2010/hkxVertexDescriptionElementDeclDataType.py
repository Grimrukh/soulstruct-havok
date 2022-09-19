from __future__ import annotations

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *


class hkxVertexDescriptionElementDeclDataType(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16
    __real_name = "hkxVertexDescriptionElementDecl::DataType"
    local_members = ()
