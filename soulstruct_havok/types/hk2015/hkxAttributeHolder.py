from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxAttributeGroup import hkxAttributeGroup


@dataclass(slots=True, eq=False, repr=False)
class hkxAttributeHolder(hkReferencedObject):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(16, "attributeGroups", hkArray(hkxAttributeGroup)),
    )
    members = hkReferencedObject.members + local_members

    attributeGroups: list[hkxAttributeGroup]
