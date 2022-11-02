from __future__ import annotations

__all__ = [
    "scale_chrbnd",
    "scale_anibnd",
    "scale_objbnd",
]

import logging
from pathlib import Path

from soulstruct.containers import Binder
from soulstruct.base.models.flver import FLVER

from .core import AnimationHKX, SkeletonHKX, RagdollHKX, ClothHKX
from .collision import CollisionHKX

_LOGGER = logging.getLogger(__name__)


def scale_chrbnd(chrbnd_path: Path | str, scale_factor: float, from_bak=True, write_path=None):
    """Scale FLVER, ragdoll, and (if present) cloth in CHRBND."""
    if write_path is None:
        write_path = chrbnd_path
    chrbnd = Binder(chrbnd_path, from_bak=from_bak)

    flver_entry = chrbnd.find_entry_matching_name(r".*\.flver")  # should be ID 200
    model = FLVER(flver_entry)
    model.scale(scale_factor)
    flver_entry.set_uncompressed_data(model.pack_dcx())
    _LOGGER.info(f"{flver_entry.name} model scaled by {scale_factor}.")

    model_name = flver_entry.name.split(".")[0]
    ragdoll_entry = chrbnd[f"{model_name}.hkx"]  # should be ID 300
    ragdoll_hkx = RagdollHKX(ragdoll_entry)
    ragdoll_hkx.scale(scale_factor)
    chrbnd[f"{model_name}.hkx"].set_uncompressed_data(ragdoll_hkx.pack_dcx())
    _LOGGER.info(f"{ragdoll_entry.name} ragdoll physics scaled by {scale_factor}.")

    try:
        cloth_entry = chrbnd.find_entry_matching_name(rf"{model_name}_c\.hkx")  # should be ID 700
    except ValueError:
        # No cloth data.
        _LOGGER.info("No cloth HKX found.")
    else:
        cloth_hkx = ClothHKX(cloth_entry)
        cloth_hkx.scale(scale_factor)
        cloth_entry.set_uncompressed_data(cloth_hkx.pack_dcx())
        _LOGGER.info(f"{cloth_entry.name} cloth physics scaled by {scale_factor}.")

    chrbnd.write(write_path)
    _LOGGER.info(f"Scaling complete. {write_path} written.")


def scale_anibnd(anibnd_path: Path | str, scale_factor: float, from_bak=True, write_path=None):
    """Scale skeleton and all animations."""
    if write_path is None:
        write_path = anibnd_path
    anibnd = Binder(anibnd_path, from_bak=from_bak)

    skeleton_entry = anibnd.find_entry_matching_name(r"[Ss]keleton\.(HKX|hkx)")  # should be ID 1000000
    skeleton_hkx = SkeletonHKX(skeleton_entry)
    skeleton_hkx.scale(scale_factor)
    skeleton_entry.set_uncompressed_data(skeleton_hkx.pack_dcx())
    _LOGGER.info(f"{skeleton_entry.name} skeleton scaled by {scale_factor}.")

    animation_entries = anibnd.find_entries_matching_name(r"a.*\.hkx")
    for entry in animation_entries:
        _LOGGER.info(f"  Scaling animation {entry.id} by {scale_factor}...")
        animation_hkx = AnimationHKX(entry)  # "aXX_XXXX.hkx"
        animation_hkx.scale(scale_factor)
        entry.set_uncompressed_data(animation_hkx.pack_dcx())

    anibnd.write(write_path)
    _LOGGER.info(f"Scaling complete. {write_path} written.")


def scale_objbnd(
    objbnd_path: Path | str, scale_factor: float, from_bak=True, write_path=None, new_model_id: int = None
):
    """Scale FLVER and HKX models."""
    if write_path is None:
        write_path = objbnd_path
    objbnd = Binder(objbnd_path, from_bak=from_bak)

    try:
        flver_entry = objbnd.find_entry_matching_name(r".*\.flver")  # should be ID 200
    except objbnd.BinderEntryMissing:
        pass  # no FLVER in this object (e.g., fog wall)
    else:
        model = FLVER(flver_entry)
        model.scale(scale_factor)
        flver_entry.set_uncompressed_data(model.pack_dcx())
        _LOGGER.info(f"{flver_entry.name} model scaled by {scale_factor}.")

    model_name = objbnd_path.name.split(".")[0]
    try:
        collision_hkx_entry = objbnd[f"{model_name}.hkx"]  # should be ID 300
    except objbnd.BinderEntryMissing:
        pass  # no collision in this object
    else:
        collision_hkx = CollisionHKX(collision_hkx_entry)
        collision_hkx.scale(scale_factor)
        objbnd[f"{model_name}.hkx"].set_uncompressed_data(collision_hkx.pack_dcx())
        _LOGGER.info(f"{collision_hkx_entry.name} object collision physics scaled by {scale_factor}.")

    if new_model_id:
        new_model_name = f"o{new_model_id}"
        for entry in objbnd.entries:
            entry.path = entry.path.replace(model_name, new_model_name)
        if not Path(write_path).name.startswith(new_model_name):
            _LOGGER.warning(f"OBJBND write path '{write_path}' does not start with new model name '{new_model_name}'.")

    objbnd.write(write_path)
    _LOGGER.info(f"Scaling complete. {write_path} written.")
