from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


class hkRootLevelContainerNamedVariant(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "className", hkStringPtr),
        Member(8, "variant", Ptr(hkReferencedObject)),
    )
    members = local_members

    name: str
    className: str
    variant: hkReferencedObject
