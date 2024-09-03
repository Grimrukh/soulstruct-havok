from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkpShape import hkpShape
from .hkpBvTreeShapeBvTreeType import hkpBvTreeShapeBvTreeType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpBvTreeShape(hkpShape):
    alignment = 8
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61

    # TODO: adjusted
    local_members = (
        Member(16, "bvTreeType", hkEnum(hkpBvTreeShapeBvTreeType, hkUint8)),
    )
    members = hkpShape.members + local_members

    bvTreeType: hkpBvTreeShapeBvTreeType
