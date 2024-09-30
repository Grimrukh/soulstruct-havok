from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from ._hknp.hknpMaterial import hknpMaterial


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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
