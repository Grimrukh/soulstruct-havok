from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpMoppCodeCodeInfo(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkpMoppCode::CodeInfo"

    local_members = (
        Member(0, "offset", hkVector4),
    )
    members = local_members

    offset: Vector4
