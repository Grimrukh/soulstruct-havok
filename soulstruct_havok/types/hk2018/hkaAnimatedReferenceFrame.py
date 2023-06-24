from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum import hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum


@dataclass(slots=True, eq=False, repr=False)
class hkaAnimatedReferenceFrame(hkReferencedObject):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(
            24,
            "frameType",
            hkEnum(hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum, hkInt8),
            MemberFlags.NotSerializable,
        ),
    )
    members = hkReferencedObject.members + local_members

    frameType: hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum
