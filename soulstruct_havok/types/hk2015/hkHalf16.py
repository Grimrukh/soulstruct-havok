from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkHalf16(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Float | TagDataType.Float16

    __tag_format_flags = 41

    local_members = (
        Member(0, "value", hkInt16, MemberFlags.Private),
    )
    members = local_members

    value: int
