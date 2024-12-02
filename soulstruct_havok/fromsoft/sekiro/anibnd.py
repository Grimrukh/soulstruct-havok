from __future__ import annotations

__all__ = ["ANIBND"]

import typing as tp
from dataclasses import dataclass, field

from soulstruct_havok.fromsoft.base.anibnd import BaseANIBND
from .core import AnimationHKX, SkeletonHKX, AnimationContainerType


@dataclass(slots=True)
class ANIBND(BaseANIBND):

    ANIMATION_HKX: tp.ClassVar = AnimationHKX
    SKELETON_HKX: tp.ClassVar = SkeletonHKX

    skeleton_hkx: SkeletonHKX | None = None
    animations_hkx: dict[int, AnimationHKX] = field(default_factory=dict)

    # Type hint override for base method.
    get_animation_container: tp.ClassVar[tp.Callable[[int | None], AnimationContainerType]]

    @staticmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        if animation_id >= 999999:
            raise ValueError("Max animation ID for DS1 is 999999.")
        return f"a{animation_id // 10000:02d}_{animation_id % 10000:04d}.hkx"
