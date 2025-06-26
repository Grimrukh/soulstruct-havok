from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hknpShapeTypeEnum import hknpShapeTypeEnum

from .hknpCollisionDispatchTypeEnum import hknpCollisionDispatchTypeEnum


from ..hkRefCountedProperties import hkRefCountedProperties


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpShape(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4

    local_members = (
        Member(20, "flags", hkFlags(hkUint16), MemberFlags.Protected),
        Member(22, "type", hkEnum(hknpShapeTypeEnum, hkUint8), MemberFlags.Protected),
        Member(23, "numShapeKeyBits", hkUint8, MemberFlags.Protected),
        Member(24, "dispatchType", hkEnum(hknpCollisionDispatchTypeEnum, hkUint8)),
        Member(28, "convexRadius", hkReal),
        Member(32, "userData", hkUint64),
        Member(40, "properties", hkRefPtr(hkRefCountedProperties, hsh=797442063), MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    flags: hkUint16
    type: hknpShapeTypeEnum
    numShapeKeyBits: int
    dispatchType: hknpCollisionDispatchTypeEnum
    convexRadius: float
    userData: int
    properties: hkRefCountedProperties
