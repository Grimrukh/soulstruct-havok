from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpLinkedCollidable import hkpLinkedCollidable
from ..hkMultiThreadCheck import hkMultiThreadCheck
from ..hkSimpleProperty import hkSimpleProperty


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpWorldObject(hkReferencedObject):
    alignment = 8
    byte_size = 200
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(16, "world", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(24, "userData", hkUlong, MemberFlags.Protected),
        Member(32, "collidable", hkpLinkedCollidable, MemberFlags.Protected),
        Member(160, "multiThreadCheck", hkMultiThreadCheck, MemberFlags.Protected),
        Member(176, "name", hkStringPtr, MemberFlags.Protected),
        Member(184, "properties", hkArray(hkSimpleProperty)),
    )
    members = hkReferencedObject.members + local_members

    world: None = None
    userData: int
    collidable: hkpLinkedCollidable
    multiThreadCheck: hkMultiThreadCheck
    name: str
    properties: list[hkSimpleProperty]
