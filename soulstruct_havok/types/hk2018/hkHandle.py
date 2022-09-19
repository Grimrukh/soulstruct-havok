from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *



class hkHandle(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "value", hkUint32, MemberFlags.Protected),
    )
    members = local_members

    value: int

    __templates = (
        TemplateType("tTYPE", type=hkUint32),
        TemplateValue("vINVALID_VALUE", value=2147483647),
    )
