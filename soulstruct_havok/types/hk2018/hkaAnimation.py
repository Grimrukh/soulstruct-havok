from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *

from .hkaAnimationAnimationType import hkaAnimationAnimationType
from .hkaAnimatedReferenceFrame import hkaAnimatedReferenceFrame
from .hkaAnnotationTrack import hkaAnnotationTrack


@dataclass(slots=True, eq=False, repr=False)
class hkaAnimation(hkReferencedObject):
    alignment = 8
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 3

    local_members = (
        Member(24, "type", hkEnum(hkaAnimationAnimationType, hkInt32), MemberFlags.Protected),
        Member(28, "duration", hkReal),
        Member(32, "numberOfTransformTracks", _int),
        Member(36, "numberOfFloatTracks", _int),
        Member(
            40,
            "extractedMotion",
            hkRefPtr(hkaAnimatedReferenceFrame, hsh=1067316339),
            MemberFlags.Protected,
        ),
        Member(48, "annotationTracks", hkArray(hkaAnnotationTrack, hsh=1044147508)),
    )
    members = hkReferencedObject.members + local_members

    type: hkaAnimationAnimationType
    duration: float
    numberOfTransformTracks: int
    numberOfFloatTracks: int
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]
