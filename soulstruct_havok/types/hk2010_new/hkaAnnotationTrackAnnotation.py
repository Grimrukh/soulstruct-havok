from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


class hkaAnnotationTrackAnnotation(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "time", hkReal),
        Member(4, "text", hkStringPtr),
    )
    members = local_members

    time: float
    text: str
