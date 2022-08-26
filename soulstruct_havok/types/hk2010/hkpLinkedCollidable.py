from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpCollidable import hkpCollidable


class hkpLinkedCollidable(hkpCollidable):
    alignment = 16
    byte_size = 92
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(80, "collisionEntries", hkArray(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = hkpCollidable.members + local_members

    collisionEntries: list
