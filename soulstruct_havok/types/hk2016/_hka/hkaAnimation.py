from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkaAnimationAnimationType import hkaAnimationAnimationType
from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame
from .hkaAnnotationTrack import hkaAnnotationTrack


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimation(hkReferencedObject):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 0
    __version = 3

    local_members = (
        Member(16, "type", hkEnum(hkaAnimationAnimationType, hkInt32), MemberFlags.Protected),
        Member(20, "duration", hkReal),
        Member(24, "numberOfTransformTracks", _int),
        Member(28, "numberOfFloatTracks", _int),
        Member(
            32,
            "extractedMotion",
            hkRefPtr(hkaAnimatedReferenceFrame, hsh=686995507),
            MemberFlags.Protected,
        ),
        Member(40, "annotationTracks", hkArray(hkaAnnotationTrack, hsh=409807455)),
    )
    members = hkReferencedObject.members + local_members

    type: int
    duration: float
    numberOfTransformTracks: int
    numberOfFloatTracks: int
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]
