from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaAnnotationTrackAnnotation import hkaAnnotationTrackAnnotation


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnnotationTrack(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "trackName", hkStringPtr),
        Member(8, "annotations", hkArray(hkaAnnotationTrackAnnotation)),
    )
    members = local_members

    trackName: str
    annotations: list[hkaAnnotationTrackAnnotation]
