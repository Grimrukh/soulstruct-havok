from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hknpShapeTagCodecType import hknpShapeTagCodecType


class hknpShapeTagCodec(hkReferencedObject):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 2

    local_members = (
        Member(20, "hints", hkFlags(hkUint32)),
        Member(24, "type", hkEnum(hknpShapeTagCodecType, hkUint8)),
    )
    members = hkReferencedObject.members + local_members

    hints: hkUint32
    type: hknpShapeTagCodecType
