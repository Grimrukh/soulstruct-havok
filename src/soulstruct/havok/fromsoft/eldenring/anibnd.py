from __future__ import annotations

import typing as tp
from dataclasses import dataclass, field

from soulstruct.havok.fromsoft.base.anibnd import BaseANIBND
from .file_types import AnimationHKX, SkeletonHKX, AnimationContainerType


class ANIBND(BaseANIBND):

    ANIMATION_HKX = AnimationHKX
    SKELETON_HKX = SkeletonHKX

    skeleton_hkx: SkeletonHKX | None = None
    animations_hkx: dict[int, AnimationHKX] = field(default_factory=dict)

    get_animation_container: tp.ClassVar[tp.Callable[[int | None], AnimationContainerType]]

    @staticmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        if animation_id >= 999999999:
            raise ValueError("Max animation ID for Elden Ring (hk2018) is 999999999.")
        return f"a{animation_id // 1000000:03d}_{animation_id % 1000000:06d}.hkx"
