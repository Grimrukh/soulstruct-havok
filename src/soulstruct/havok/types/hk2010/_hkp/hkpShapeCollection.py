from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpShape import hkpShape
from .hkpShapeCollectionCollectionType import hkpShapeCollectionCollectionType
from .hkpShapeContainer import hkpShapeContainer


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpShapeCollection(hkpShape):
    alignment = 8
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 121

    # TODO: adjusted
    local_members = (
        Member(16, "disableWelding", hkBool),
        Member(17, "collectionType", hkEnum(hkpShapeCollectionCollectionType, hkUint8)),
    )
    members = hkpShape.members + local_members

    disableWelding: bool
    collectionType: hkpShapeCollectionCollectionType

    __interfaces = (
        Interface(hkpShapeContainer, flags=32),
    )
