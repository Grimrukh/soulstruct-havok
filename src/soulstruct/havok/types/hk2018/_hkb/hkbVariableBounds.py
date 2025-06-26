from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbVariableValue import hkbVariableValue


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbVariableBounds(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1452260632

    local_members = (
        Member(0, "min", hkbVariableValue),
        Member(4, "max", hkbVariableValue),
    )
    members = local_members

    min: hkbVariableValue
    max: hkbVariableValue
