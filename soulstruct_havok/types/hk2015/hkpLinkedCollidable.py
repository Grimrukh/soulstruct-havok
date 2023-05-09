from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkpCollidable import hkpCollidable


@dataclass(slots=True, eq=False, repr=False)
class hkpLinkedCollidable(hkpCollidable):
    alignment = 8
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(
            112,
            "collisionEntries",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
    )
    members = hkpCollidable.members + local_members

    collisionEntries: list[hkReflectDetailOpaque]
