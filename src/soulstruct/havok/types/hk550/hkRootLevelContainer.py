from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .hkRootLevelContainerNamedVariant import hkRootLevelContainerNamedVariant
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRootLevelContainer(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4120421198

    local_members = (
        Member(0, "namedVariants", hkArray(hkRootLevelContainerNamedVariant, flags=0, forced_capacity=0)),
    )
    members = local_members

    namedVariants: list[hkRootLevelContainerNamedVariant]
