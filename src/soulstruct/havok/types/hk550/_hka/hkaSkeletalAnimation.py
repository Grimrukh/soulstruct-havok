from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaAnimationAnimationType import hkaAnimationAnimationType
from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame
from .hkaAnnotationTrack import hkaAnnotationTrack


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeletalAnimation(hkReferencedObject):
    alignment = 4
    byte_size = 36
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2566467901

    local_members = (
        Member(8, "type", hkEnum(hkaAnimationAnimationType, hkInt32)),
        Member(12, "duration", hkReal),
        Member(16, "numberOfTransformTracks", _int),
        Member(20, "numberOfFloatTracks", _int),
        Member(24, "extractedMotion", Ptr(hkaAnimatedReferenceFrame)),
        Member(28, "annotationTracks", SimpleArray(hkaAnnotationTrack)),
    )
    members = hkReferencedObject.members + local_members

    type: int
    duration: float
    numberOfTransformTracks: int
    numberOfFloatTracks: int
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]
