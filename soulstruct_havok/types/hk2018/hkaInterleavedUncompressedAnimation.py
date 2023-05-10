from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkaAnimation import hkaAnimation
from .hkaSplineCompressedAnimation import hkaSplineCompressedAnimation


@dataclass(slots=True, eq=False, repr=False)
class hkaInterleavedUncompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 88
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3449291259  # TODO: may be wrong for 2018 (from TagTools; could be 2014 only)
    __version = 1

    local_members = (
        Member(56, "transforms", hkArray(hkQsTransform), MemberFlags.Private),
        Member(72, "floats", hkArray(hkReal), MemberFlags.Private),
    )
    members = hkaAnimation.members + local_members

    transforms: list[hkQsTransform]
    floats: list[float]

    @classmethod
    def from_spline_animation(cls, spline_animation: hkaSplineCompressedAnimation, transforms: list[hkQsTransform]):
        """Converts a spline animation to an uncompressed animation."""
        return cls(
            memSizeAndFlags=0,
            refCount=0,
            propertyBag=None,
            type=1,  # correct for all Havok versions
            duration=spline_animation.duration,
            numberOfTransformTracks=spline_animation.numberOfTransformTracks,
            numberOfFloatTracks=spline_animation.numberOfFloatTracks,
            extractedMotion=spline_animation.extractedMotion,
            annotationTracks=spline_animation.annotationTracks,
            transforms=transforms,
            floats=[],  # TODO: Not sure if this is ever used.
        )
