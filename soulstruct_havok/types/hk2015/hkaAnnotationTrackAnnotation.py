from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkaAnnotationTrackAnnotation(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkaAnnotationTrack::Annotation"

    local_members = (
        Member(0, "time", hkReal),
        Member(8, "text", hkStringPtr),
    )
    members = local_members

    time: float
    text: str
