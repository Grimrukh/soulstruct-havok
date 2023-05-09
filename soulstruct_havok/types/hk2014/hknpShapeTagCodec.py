from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hknpShapeTagCodecType import hknpShapeTagCodecType


@dataclass(slots=True, eq=False, repr=False)
class hknpShapeTagCodec(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(16, "type", hkEnum(hknpShapeTagCodecType, hkUint8)),
    )
    members = hkReferencedObject.members + local_members

    type: int
