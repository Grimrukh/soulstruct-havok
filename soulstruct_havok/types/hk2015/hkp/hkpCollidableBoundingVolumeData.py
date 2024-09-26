from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpCollidableBoundingVolumeData(hk):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpCollidable::BoundingVolumeData"

    local_members = (
        Member(0, "min", hkGenericStruct(hkUint32, 3)),
        Member(12, "expansionMin", hkGenericStruct(hkUint8, 3)),
        Member(15, "expansionShift", hkUint8),
        Member(16, "max", hkGenericStruct(hkUint32, 3)),
        Member(28, "expansionMax", hkGenericStruct(hkUint8, 3)),
        Member(31, "padding", hkUint8, MemberFlags.NotSerializable),
        Member(32, "numChildShapeAabbs", hkUint16, MemberFlags.NotSerializable),
        Member(34, "capacityChildShapeAabbs", hkUint16, MemberFlags.NotSerializable),
        Member(40, "childShapeAabbs", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(48, "childShapeKeys", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = local_members

    min: tuple[int, int, int]
    expansionMin: tuple[int, int, int]
    expansionShift: int
    max: tuple[int, int, int]
    expansionMax: tuple[int, int, int]
    padding: int
    numChildShapeAabbs: int
    capacityChildShapeAabbs: int
    childShapeAabbs: None = None
    childShapeKeys: None = None
