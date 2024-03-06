from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkRootLevelContainerNamedVariant import hkRootLevelContainerNamedVariant


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRootLevelContainer(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2517046881

    local_members = (
        Member(0, "namedVariants", hkArray(hkRootLevelContainerNamedVariant, hsh=188352321)),
    )
    members = local_members

    namedVariants: list[hkRootLevelContainerNamedVariant]
