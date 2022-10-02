from __future__ import annotations

from soulstruct_havok.types.hk2015 import hkaInterleavedUncompressedAnimation
from soulstruct_havok.wrappers.base.animation_manager import BaseAnimationManager


class AnimationManager(BaseAnimationManager):

    def convert_spline_anim_to_interleaved(self, anim_id: int = None):
        """Convert a spline-compressed animation to 'interleaved' format, which is just a raw list of frame"""
        if anim_id is None:
            anim_id = self.get_default_anim_id()
        self.check_data_loaded(anim_id)

    @staticmethod
    def animation_id_to_entry_basename(animation_id: int) -> str:
        if animation_id >= 999999:
            raise ValueError("Max animation ID for DS1 is 999999.")
        return f"a{animation_id // 10000:02d}_{animation_id % 10000:04d}.hkx"
