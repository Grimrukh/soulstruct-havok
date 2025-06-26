from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hknpShapeEnum import hknpShapeEnum
from ..hkRefCountedProperties import hkRefCountedProperties


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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
        Member(40, "pad", hkUint64),  # TODO: Not a real member, so might cause TypeInfo errors.
    )
    members = hkReferencedObject.members + local_members

    flags: int
    numShapeKeyBits: int
    dispatchType: int
    convexRadius: float
    userData: int
    properties: hkRefCountedProperties
    pad: int = 0
