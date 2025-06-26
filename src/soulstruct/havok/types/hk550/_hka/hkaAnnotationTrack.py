from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaAnnotationTrackAnnotation import hkaAnnotationTrackAnnotation


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnnotationTrack(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2221917840

    local_members = (
        Member(0, "trackName", hkStringPtr),
        Member(4, "annotations", SimpleArray(hkaAnnotationTrackAnnotation)),
    )
    members = local_members

    trackName: str
    annotations: list[hkaAnnotationTrackAnnotation]
