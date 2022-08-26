from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpCollisionFilterhkpFilterType import hkpCollisionFilterhkpFilterType
from .hkpCollidableCollidableFilter import hkpCollidableCollidableFilter
from .hkpShapeCollectionFilter import hkpShapeCollectionFilter
from .hkpRayShapeCollectionFilter import hkpRayShapeCollectionFilter
from .hkpRayCollidableFilter import hkpRayCollidableFilter


class hkpCollisionFilter(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 121
    __abstract_value = 3

    local_members = (
        Member(48, "prepad", hkGenericStruct(hkUint32, 2)),
        Member(56, "type", hkEnum(hkpCollisionFilterhkpFilterType, hkUint32)),
        Member(60, "postpad", hkGenericStruct(hkUint32, 3)),
    )
    members = hkReferencedObject.members + local_members

    prepad: tuple[hkUint32]
    type: hkpCollisionFilterhkpFilterType
    postpad: tuple[hkUint32]

    __interfaces = (
        Interface(hkpCollidableCollidableFilter, flags=16),
        Interface(hkpShapeCollectionFilter, flags=24),
        Interface(hkpRayShapeCollectionFilter, flags=32),
        Interface(hkpRayCollidableFilter, flags=40),
    )
