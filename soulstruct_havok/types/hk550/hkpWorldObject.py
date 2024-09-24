from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpLinkedCollidable import hkpLinkedCollidable
from .hkMultiThreadCheck import hkMultiThreadCheck
from .hkpProperty import hkpProperty


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpWorldObject(hkReferencedObject):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "world", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(12, "userData", hkUlong),
        Member(16, "collidable", hkpLinkedCollidable),
        Member(104, "multiThreadCheck", hkMultiThreadCheck),
        Member(112, "name", hkStringPtr),
        Member(116, "properties", hkArray(hkpProperty)),
    )
    members = hkReferencedObject.members + local_members

    world: None
    userData: int
    collidable: hkpLinkedCollidable
    multiThreadCheck: hkMultiThreadCheck
    name: str
    properties: list[hkpProperty]
