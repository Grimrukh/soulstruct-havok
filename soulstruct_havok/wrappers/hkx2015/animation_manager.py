from __future__ import annotations

import typing as tp

from soulstruct.containers.bnd import BND3

from soulstruct_havok.wrappers.base.animation_manager import BaseANIBND
from .core import AnimationHKX, SkeletonHKX


class ANIBND(BaseANIBND, BND3):

    ANIMATION_HKX = AnimationHKX
    SKELETON_HKX = SkeletonHKX
    skeleton: SkeletonHKX
    animations: dict[int, AnimationHKX]

    get_animation: tp.Callable[[tp.Optional[int]], AnimationHKX]

    def convert_interleaved_to_spline_anim(self, anim_id: int = None):
        """Convert to spline animation by a downgrade -> SDK conversion -> upgrade process."""
        animation = self.get_animation(anim_id)
        spline_anim = animation.to_spline_animation()
        self.animations[anim_id] = spline_anim

    @staticmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        if animation_id >= 999999:
            raise ValueError("Max animation ID for DS1 is 999999.")
        return f"a{animation_id // 10000:02d}_{animation_id % 10000:04d}.hkx"
