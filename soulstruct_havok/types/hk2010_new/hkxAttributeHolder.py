from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxAttributeGroup import hkxAttributeGroup


class hkxAttributeHolder(hkReferencedObject):
    alignment = 16
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "attributeGroups", hkArray(hkxAttributeGroup)),
    )
    members = hkReferencedObject.members + local_members

    attributeGroups: list[hkxAttributeGroup]
