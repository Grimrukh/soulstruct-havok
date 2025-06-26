from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbRoleAttribute import hkbRoleAttribute
from .hkbVariableInfoVariableType import hkbVariableInfoVariableType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbVariableInfo(hk):
    alignment = 2
    byte_size = 6
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3541396085
    __version = 1

    local_members = (
        Member(0, "role", hkbRoleAttribute),
        Member(4, "type", hkEnum(hkbVariableInfoVariableType, hkInt8)),
    )
    members = local_members

    role: hkbRoleAttribute
    type: hkbVariableInfoVariableType
