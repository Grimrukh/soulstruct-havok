from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkRootLevelContainerNamedVariant import hkRootLevelContainerNamedVariant


@dataclass(slots=True, eq=False, repr=False)
class hkRootLevelContainer(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 661831966

    local_members = (
        Member(0, "namedVariants", hkArray(hkRootLevelContainerNamedVariant)),
    )
    members = local_members

    namedVariants: list[hkRootLevelContainerNamedVariant]
