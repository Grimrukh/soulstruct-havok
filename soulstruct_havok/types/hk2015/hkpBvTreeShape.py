from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpShape import hkpShape
from .hkpBvTreeShapeBvTreeType import hkpBvTreeShapeBvTreeType


class hkpBvTreeShape(hkpShape):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1

    local_members = (
        Member(32, "bvTreeType", hkEnum(hkpBvTreeShapeBvTreeType, hkUint8)),
    )
    members = hkpShape.members + local_members

    bvTreeType: hkpBvTreeShapeBvTreeType