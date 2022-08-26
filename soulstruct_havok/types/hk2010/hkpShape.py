from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpShapeShapeType import hkpShapeShapeType


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
    type: int
