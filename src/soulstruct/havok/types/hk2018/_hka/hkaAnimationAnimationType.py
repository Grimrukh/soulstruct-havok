from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimationAnimationType(hk):
    """
    /// Type information
    enum AnimationType {
            /// Should never be used
        HK_UNKNOWN_ANIMATION = 0,
            /// Interleaved
        HK_INTERLEAVED_ANIMATION,
            /// Mirrored
        HK_MIRRORED_ANIMATION,
            /// Spline
        HK_SPLINE_COMPRESSED_ANIMATION,
            /// Quantized
        HK_QUANTIZED_COMPRESSED_ANIMATION,
            /// Predictive
        HK_PREDICTIVE_COMPRESSED_ANIMATION,
            /// Reference Pose
        HK_REFERENCE_POSE_ANIMATION,
    };
    """
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkaAnimation::AnimationType"
    local_members = ()

    CLASS_NAMES = {
        1: "hkaInterleavedUncompressedAnimation",
        2: "hkaMirroredAnimation",
        3: "hkaSplineCompressedAnimation",
        4: "hkaQuantizedCompressedAnimation",
        5: "hkaPredictiveCompressedAnimation",
        6: "hkaReferencePoseAnimation",
    }

    @staticmethod
    def from_older_enum(old_value: int) -> int:
        """Enum for animation type changed sometime between 2010 (PTDE) and 2014 (BB)."""
        try:
            return {
                1: 1,  # hkaInterleavedUncompressedAnimation
                4: 2,  # hkaMirroredAnimation
                5: 3,  # hkaSplineCompressedAnimation
            }[old_value]
        except KeyError:
            raise ValueError(f"Old animation type enum value {old_value} not recognized. Cannot convert to new value.")
