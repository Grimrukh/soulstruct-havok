from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimationAnimationType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkaAnimation::AnimationType"
    local_members = ()

    NAMES = {
        2: "hkaMirroredAnimation",
        3: "hkaSplineCompressedAnimation",
        4: "hkaQuantizedAnimation",
        5: "hkaPredictiveAnimation",
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
            raise ValueError(f"Old animation type enum value {old_value} not recognized. Cannot convert to 2016.")
