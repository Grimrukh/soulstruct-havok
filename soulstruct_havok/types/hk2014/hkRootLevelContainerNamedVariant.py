from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkRootLevelContainerNamedVariant(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "className", hkStringPtr),
        Member(16, "variant", Ptr(hkReferencedObject)),
    )
    members = local_members

    name: str
    className: str
    variant: hkReferencedObject
