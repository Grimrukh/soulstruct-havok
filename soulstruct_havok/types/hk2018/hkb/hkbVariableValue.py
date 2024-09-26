from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbVariableValue(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3199650346

    local_members = (
        Member(0, "value", _int, MemberFlags.Private),
    )
    members = local_members

    value: int
