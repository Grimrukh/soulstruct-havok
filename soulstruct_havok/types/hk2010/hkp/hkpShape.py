from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpShapeShapeType import hkpShapeShapeType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpShape(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "userData", hkUlong),
        Member(12, "type", hkEnum(hkpShapeShapeType, hkUint32), MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    userData: int
    type: int = 0
