from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkSimplePropertyValue(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "data", hkUint64),
    )
    members = local_members

    data: int
