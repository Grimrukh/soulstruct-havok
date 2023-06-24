from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpCollisionFilterhkpFilterType import hkpCollisionFilterhkpFilterType


@dataclass(slots=True, eq=False, repr=False)
class hkpCollisionFilter(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(24, "prepad", hkStruct(hkUint32, 2)),
        Member(32, "type", hkEnum(hkpCollisionFilterhkpFilterType, hkUint32)),
        Member(36, "postpad", hkStruct(hkUint32, 3)),
    )
    members = hkReferencedObject.members + local_members

    prepad: tuple[int, ...]
    type: int
    postpad: tuple[int, ...]
