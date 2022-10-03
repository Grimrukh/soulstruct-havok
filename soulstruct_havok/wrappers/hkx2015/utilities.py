from __future__ import annotations

__all__ = [
    "scale_chrbnd",
    "scale_anibnd",
]

import logging
from pathlib import Path

from soulstruct.containers import Binder
from soulstruct.base.models.flver import FLVER

from soulstruct_havok.wrappers.base import BaseAnimationHKX, BaseSkeletonHKX, BaseRagdollHKX, BaseClothHKX

_LOGGER = logging.getLogger(__name__)


def scale_chrbnd(chrbnd_path: Path | str, scale_factor: float, from_bak=True):
    """Scale FLVER, ragdoll, and (if present) cloth in CHRBND."""
    chrbnd = Binder(chrbnd_path, from_bak=from_bak)

    flver_entry = chrbnd.find_entry_matching_name(r".*\.flver")  # should be ID 200
    model = FLVER(flver_entry)
    model.scale(scale_factor)
    flver_entry.set_uncompressed_data(model.pack_dcx())
    _LOGGER.info(f"{flver_entry.name} model scaled by {scale_factor}.")

    model_name = flver_entry.name.split(".")[0]
    ragdoll_entry = chrbnd[f"{model_name}.hkx"]  # should be ID 300
    ragdoll_hkx = BaseRagdollHKX(ragdoll_entry)
    ragdoll_hkx.scale(scale_factor)
    chrbnd[f"{model_name}.hkx"].set_uncompressed_data(ragdoll_hkx.pack_dcx())
    _LOGGER.info(f"{ragdoll_entry.name} ragdoll physics scaled by {scale_factor}.")

    try:
        cloth_entry = chrbnd.find_entry_matching_name(rf"{model_name}_c\.hkx")  # should be ID 700
    except KeyError:
        # No cloth data.
        _LOGGER.info("No cloth HKX found.")
    else:
        cloth_hkx = BaseClothHKX(cloth_entry)
        cloth_hkx.scale(scale_factor)
        cloth_entry.set_uncompressed_data(cloth_hkx.pack_dcx())
        _LOGGER.info(f"{cloth_entry.name} cloth physics scaled by {scale_factor}.")

    chrbnd.write()
    _LOGGER.info(f"Scaling complete. {chrbnd.path} written.")


def scale_anibnd(anibnd_path: Path | str, scale_factor: float, from_bak=True):
    """Scale skeleton and all animations."""
    anibnd = Binder(anibnd_path, from_bak=from_bak)

    skeleton_entry = anibnd.find_entry_matching_name(r"[Ss]keleton\.(HKX|hkx)")  # should be ID 1000000
    skeleton_hkx = BaseSkeletonHKX(skeleton_entry)
    skeleton_hkx.scale(scale_factor)
    skeleton_entry.set_uncompressed_data(skeleton_hkx.pack_dcx())
    _LOGGER.info(f"{skeleton_entry.name} skeleton scaled by {scale_factor}.")

    animation_entries = anibnd.find_entries_matching_name(r"a.*\.hkx")
    for entry in animation_entries:
        _LOGGER.info(f"  Scaling animation {entry.id} by {scale_factor}...")
        animation_hkx = BaseAnimationHKX(entry)  # "aXX_XXXX.hkx"
        animation_hkx.scale(scale_factor)
        entry.set_uncompressed_data(animation_hkx.pack_dcx())

    anibnd.write()
    _LOGGER.info(f"Scaling complete. {anibnd.path} written.")
