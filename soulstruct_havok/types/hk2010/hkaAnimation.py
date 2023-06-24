from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkaAnimationAnimationType import hkaAnimationAnimationType
from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame
from .hkaAnnotationTrack import hkaAnnotationTrack


@dataclass(slots=True, eq=False, repr=False)
class hkaAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "type", hkEnum(hkaAnimationAnimationType, hkInt32)),
        Member(12, "duration", hkReal),
        Member(16, "numberOfTransformTracks", hkInt32),
        Member(20, "numberOfFloatTracks", hkInt32),
        Member(24, "extractedMotion", Ptr(hkaAnimatedReferenceFrame)),
        Member(28, "annotationTracks", hkArray(hkaAnnotationTrack)),
    )
    members = hkReferencedObject.members + local_members

    type: int
    duration: float
    numberOfTransformTracks: int
    numberOfFloatTracks: int
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]
