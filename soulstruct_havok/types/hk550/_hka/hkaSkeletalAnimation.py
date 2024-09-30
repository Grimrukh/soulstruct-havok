from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkaAnimationAnimationType import hkaAnimationAnimationType
from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame
from .hkaAnnotationTrack import hkaAnnotationTrack


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeletalAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 36
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "type", hkEnum(hkaAnimationAnimationType, hkInt32)),
        Member(12, "duration", hkReal),
        Member(16, "numberOfTracks", hkInt32),
        Member(20, "extractedMotion", Ptr(hkaAnimatedReferenceFrame)),
        Member(24, "annotationTracks", hkArray(hkaAnnotationTrack)),
    )
    members = hkReferencedObject.members + local_members

    type: int
    duration: float
    numberOfTracks: int
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]
