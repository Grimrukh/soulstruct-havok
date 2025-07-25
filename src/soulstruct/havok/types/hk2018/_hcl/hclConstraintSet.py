from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from ..hkHandle import hkHandle


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclConstraintSet(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "constraintId", hkHandle),
        Member(36, "type", _unsigned_int, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    constraintId: hkHandle
    type: int
