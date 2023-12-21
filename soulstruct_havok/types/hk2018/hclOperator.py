from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hclClothStateBufferAccess import hclClothStateBufferAccess
from .hclClothStateTransformSetAccess import hclClothStateTransformSetAccess


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclOperator(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 2

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "operatorID", _unsigned_int),
        Member(36, "type", _unsigned_int, MemberFlags.NotSerializable),
        Member(40, "usedBuffers", hkArray(hclClothStateBufferAccess, hsh=686371003)),
        Member(56, "usedTransformSets", hkArray(hclClothStateTransformSetAccess, hsh=1767586432)),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    operatorID: int
    type: int
    usedBuffers: list[hclClothStateBufferAccess]
    usedTransformSets: list[hclClothStateTransformSetAccess]
