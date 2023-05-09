from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum import hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum


@dataclass(slots=True, eq=False, repr=False)
class hkaAnimatedReferenceFrame(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(
            16,
            "frameType",
            hkEnum(hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum, hkInt8),
            MemberFlags.NotSerializable,
        ),
    )
    members = hkReferencedObject.members + local_members

    frameType: int
