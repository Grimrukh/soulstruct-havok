from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRootLevelContainerNamedVariant(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3786125824
    __version = 1
    __real_name = "hkRootLevelContainer::NamedVariant"

    local_members = (
        Member(0, "name", hkStringPtr, MemberFlags.Private),
        Member(8, "className", hkStringPtr, MemberFlags.Private),
        Member(16, "variant", hkRefVariant(hkReferencedObject, hsh=2872857893), MemberFlags.Private),
    )
    members = local_members

    name: str
    className: str
    variant: hkReferencedObject
