from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkMeshBoneIndexMapping(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "mapping", hkArray(hkInt16, hsh=3571075457)),
    )
    members = local_members

    mapping: list[int]
