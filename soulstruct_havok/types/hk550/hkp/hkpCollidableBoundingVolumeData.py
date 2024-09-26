from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpCollidableBoundingVolumeData(hk):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "min", hkStruct(hkUint32, 3)),
        Member(12, "expansionMin", hkStruct(hkUint8, 3)),
        Member(15, "expansionShift", hkUint8),
        Member(16, "max", hkStruct(hkUint32, 3)),
        Member(28, "expansionMax", hkStruct(hkUint8, 3)),
        Member(31, "padding", hkUint8),
        Member(32, "numChildShapeAabbs", hkUint16, MemberFlags.NotSerializable),
        Member(36, "childShapeAabbs", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = local_members

    min: tuple[int, ...]
    expansionMin: tuple[int, ...]
    expansionShift: int
    max: tuple[int, ...]
    expansionMax: tuple[int, ...]
    padding: int
    numChildShapeAabbs: int
    childShapeAabbs: None
