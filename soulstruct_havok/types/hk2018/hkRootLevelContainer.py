from __future__ import annotations

from soulstruct_havok.enums import *
from soulstruct_havok.types.core import *
from .hkRootLevelContainerNamedVariant import hkRootLevelContainerNamedVariant


class hkRootLevelContainer(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2700707004

    local_members = (
        Member(0, "namedVariants", hkArray(hkRootLevelContainerNamedVariant, hsh=2159475074)),
    )
    members = local_members

    namedVariants: list[hkRootLevelContainerNamedVariant]
