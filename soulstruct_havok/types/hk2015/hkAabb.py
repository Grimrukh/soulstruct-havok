from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkAabb(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "min", hkVector4),
        Member(16, "max", hkVector4),
    )
    members = local_members

    min: Vector4
    max: Vector4
