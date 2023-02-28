from __future__ import annotations

import typing as tp
from dataclasses import dataclass, field

from soulstruct_havok.wrappers.base.anibnd import BaseANIBND
from soulstruct_havok.wrappers.base.animation import AnimationContainer
from .file_types import AnimationHKX, SkeletonHKX


@dataclass(slots=True)
class ANIBND(BaseANIBND):

    ANIMATION_HKX: tp.ClassVar = AnimationHKX
    SKELETON_HKX: tp.ClassVar = SkeletonHKX

    skeleton_hkx: SkeletonHKX | None = None
    animations_hkx: dict[int, AnimationHKX] = field(default_factory=dict)

    get_animation_container: tp.ClassVar[tp.Callable[[int | None], AnimationContainer]]

    def convert_interleaved_to_spline_anim(self, anim_id: int = None):
        """Convert to spline animation by a downgrade -> SDK conversion -> upgrade process."""
        animation = self.get_animation(anim_id)
        spline_anim = animation.to_spline_animation()
        self._animations_hkx[anim_id] = spline_anim

    @staticmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        if animation_id >= 999999:
            raise ValueError("Max animation ID for DS1 is 999999.")
        return f"a{animation_id // 10000:02d}_{animation_id % 10000:04d}.hkx"
