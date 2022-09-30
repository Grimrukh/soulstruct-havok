from __future__ import annotations

from soulstruct_havok.wrappers.base.animation_manager import BaseAnimationManager


class AnimationManager(BaseAnimationManager):

    @staticmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        if animation_id >= 999999:
            raise ValueError("Max animation ID for ER is 999999999.")
        return f"a{animation_id // 1000000:03d}_{animation_id % 1000000:06d}.hkx"
