from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkaAnimationAnimationType import hkaAnimationAnimationType
from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame
from .hkaAnnotationTrack import hkaAnnotationTrack


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimation(hkReferencedObject):
    alignment = 4
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    # NOTE: Weird alignment. The class as a whole is only 4-byte aligned (evident from starting at 12), but the
    # `extractedMotion` pointer is 8-byte aligned.
    local_members = (
        Member(12, "type", hkEnum(hkaAnimationAnimationType, hkInt32)),
        Member(16, "duration", hkReal),
        Member(20, "numberOfTransformTracks", hkInt32),
        Member(24, "numberOfFloatTracks", hkInt32),
        Member(28, "pad_align", hkInt32, MemberFlags.NotSerializable),
        Member(32, "extractedMotion", Ptr(hkaAnimatedReferenceFrame)),
        Member(40, "annotationTracks", hkArray(hkaAnnotationTrack)),
    )
    members = hkReferencedObject.members + local_members

    type: int
    duration: float
    numberOfTransformTracks: int
    numberOfFloatTracks: int
    pad_align: int = 0
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]
