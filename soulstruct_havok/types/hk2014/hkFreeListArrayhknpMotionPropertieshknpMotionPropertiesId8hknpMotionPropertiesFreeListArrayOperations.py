from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from ._hknp.hknpMotionProperties import hknpMotionProperties


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "elements", hkArray(hknpMotionProperties)),
        Member(16, "firstFree", hkInt32),
    )
    members = local_members

    elements: list[hknpMotionProperties]
    firstFree: int
