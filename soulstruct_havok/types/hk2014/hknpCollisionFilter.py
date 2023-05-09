from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hknpCollisionFilterType import hknpCollisionFilterType


@dataclass(slots=True, eq=False, repr=False)
class hknpCollisionFilter(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "type", hkEnum(hknpCollisionFilterType, hkUint8)),
    )
    members = hkReferencedObject.members + local_members

    type: int
