from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkcdShapeTypeShapeTypeEnum import hkcdShapeTypeShapeTypeEnum
from .hkcdShapeDispatchTypeShapeDispatchTypeEnum import hkcdShapeDispatchTypeShapeDispatchTypeEnum
from .hkcdShapeInfoCodecTypeShapeInfoCodecTypeEnum import hkcdShapeInfoCodecTypeShapeInfoCodecTypeEnum


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdShape(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "type", hkEnum(hkcdShapeTypeShapeTypeEnum, hkUint8), MemberFlags.NotSerializable),
        Member(17, "dispatchType", hkEnum(hkcdShapeDispatchTypeShapeDispatchTypeEnum, hkUint8)),
        Member(18, "bitsPerKey", hkUint8),
        Member(19, "shapeInfoCodecType", hkEnum(hkcdShapeInfoCodecTypeShapeInfoCodecTypeEnum, hkUint8)),
    )
    members = hkReferencedObject.members + local_members

    type: int = 0
    dispatchType: int
    bitsPerKey: int
    shapeInfoCodecType: int
