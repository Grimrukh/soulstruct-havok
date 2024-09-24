from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpCollidable import hkpCollidable


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpLinkedCollidable(hkpCollidable):
    alignment = 16
    byte_size = 88
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(76, "collisionEntries", hkArray(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = hkpCollidable.members + local_members

    collisionEntries: list
