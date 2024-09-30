from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbRoleAttributeRole import hkbRoleAttributeRole


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbRoleAttribute(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 256

    local_members = (
        Member(0, "role", hkEnum(hkbRoleAttributeRole, hkInt16)),
        Member(2, "flags", hkFlags(hkInt16)),
    )
    members = local_members

    role: hkbRoleAttributeRole
    flags: hkInt16
