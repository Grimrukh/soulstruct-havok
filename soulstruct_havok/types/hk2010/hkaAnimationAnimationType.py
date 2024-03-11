from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimationAnimationType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32
    __real_name = "hkaAnimation::AnimationType"
    local_members = ()

    NAMES = {
        2: "hkaDeltaCompressedAnimation",
        3: "hkaWaveletCompressedAnimation",
        4: "hkaMirroredAnimation",
        5: "hkaSplineCompressedAnimation",
    }

    @staticmethod
    def from_newer_enum(new_value: int) -> int:
        """Enum for animation type changed sometime between 2010 (PTDE) and 2014 (BB)."""
        try:
            return {
                1: 1,  # hkaInterleavedUncompressedAnimation
                2: 2,  # hkaMirroredAnimation
                3: 5,  # hkaSplineCompressedAnimation
            }[new_value]
        except KeyError:
            raise ValueError(f"New animation type enum value {new_value} not recognized. Cannot convert to 2010.")
