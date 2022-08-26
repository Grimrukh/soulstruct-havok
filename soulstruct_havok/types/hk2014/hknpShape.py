from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hknpShapeEnum import hknpShapeEnum
from .hkRefCountedProperties import hkRefCountedProperties


class hknpShape(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(16, "flags", hkFlags(hkUint16)),
        Member(18, "numShapeKeyBits", hkUint8),
        Member(19, "dispatchType", hkEnum(hknpShapeEnum, hkUint8)),
        Member(20, "convexRadius", hkReal),
        Member(24, "userData", hkUint64),
        Member(32, "properties", Ptr(hkRefCountedProperties)),
    )
    members = hkReferencedObject.members + local_members

    flags: int
    numShapeKeyBits: int
    dispatchType: int
    convexRadius: float
    userData: int
    properties: hkRefCountedProperties
