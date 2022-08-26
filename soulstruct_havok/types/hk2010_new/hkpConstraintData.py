from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


class hkpConstraintData(hkReferencedObject):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "userData", hkUlong),
    )
    members = hkReferencedObject.members + local_members

    userData: int
