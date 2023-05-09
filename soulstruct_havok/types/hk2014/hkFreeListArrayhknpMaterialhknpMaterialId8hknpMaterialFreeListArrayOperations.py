from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hknpMaterial import hknpMaterial


@dataclass(slots=True, eq=False, repr=False)
class hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "elements", hkArray(hknpMaterial)),
        Member(16, "firstFree", hkInt32),
    )
    members = local_members

    elements: list[hknpMaterial]
    firstFree: int
