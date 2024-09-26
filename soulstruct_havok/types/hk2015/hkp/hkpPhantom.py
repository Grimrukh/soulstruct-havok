from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpWorldObject import hkpWorldObject


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpPhantom(hkpWorldObject):
    alignment = 8
    byte_size = 232
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(
            200,
            "overlapListeners",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            216,
            "phantomListeners",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
    )
    members = hkpWorldObject.members + local_members

    overlapListeners: list[hkReflectDetailOpaque]
    phantomListeners: list[hkReflectDetailOpaque]
