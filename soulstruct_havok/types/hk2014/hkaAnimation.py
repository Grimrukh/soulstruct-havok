from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkaAnimationAnimationType import hkaAnimationAnimationType
from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame
from .hkaAnnotationTrack import hkaAnnotationTrack


@dataclass(slots=True, eq=False, repr=False)
class hkaAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(16, "type", hkEnum(hkaAnimationAnimationType, hkInt32)),
        Member(20, "duration", hkReal),
        Member(24, "numberOfTransformTracks", hkInt32),
        Member(28, "numberOfFloatTracks", hkInt32),
        Member(32, "extractedMotion", Ptr(hkaAnimatedReferenceFrame)),
        Member(40, "annotationTracks", hkArray(hkaAnnotationTrack)),
    )
    members = hkReferencedObject.members + local_members

    type: int
    duration: float
    numberOfTransformTracks: int
    numberOfFloatTracks: int
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]
