from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hknpCollisionFilterType import hknpCollisionFilterType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpCollisionFilter(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(20, "type", hkEnum(hknpCollisionFilterType, hkUint8)),
    )
    members = hkReferencedObject.members + local_members

    type: hknpCollisionFilterType
