from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxVertexDescriptionElementDeclDataType(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16
    __real_name = "hkxVertexDescriptionElementDecl::DataType"
    local_members = ()
