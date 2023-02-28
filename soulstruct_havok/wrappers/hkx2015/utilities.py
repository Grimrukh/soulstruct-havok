from __future__ import annotations

__all__ = [
    "scale_chrbnd",
    "scale_anibnd",
    "scale_objbnd",
    "scale_character_files",
    "reverse_animation_in_anibnd_file",
    "get_animation_file_stem",
]

import logging
from pathlib import Path

from soulstruct.containers import Binder, BinderEntryNotFoundError
from soulstruct.base.models.flver import FLVER

from .file_types import AnimationHKX, SkeletonHKX, RagdollHKX, ClothHKX, CollisionHKX

_LOGGER = logging.getLogger(__name__)


def scale_chrbnd(chrbnd: Binder, scale_factor: float):
    """Scale FLVER, ragdoll, and (if present) cloth in CHRBND in-place."""
    flver_entry = chrbnd.find_entry_matching_name(r".*\.flver")
    if flver_entry.entry_id != 200:
        _LOGGER.warning(f"FLVER entry ID is {flver_entry.entry_id}, not 200.")
    model = flver_entry.to_game_file(FLVER)
    model.scale_all_translations(scale_factor)
    flver_entry.set_from_game_file(model)
    _LOGGER.info(f"{flver_entry.name} model scaled by {scale_factor}.")

    model_name = flver_entry.name.split(".")[0]
    ragdoll_entry = chrbnd[f"{model_name}.hkx"]
    if ragdoll_entry.entry_id != 300:
        _LOGGER.warning(f"Ragdoll entry ID is {ragdoll_entry.entry_id}, not 300.")
    ragdoll_hkx = ragdoll_entry.to_game_file(RagdollHKX)
    ragdoll_hkx.scale_all_translations(scale_factor)
    chrbnd[f"{model_name}.hkx"].set_from_game_file(ragdoll_hkx)
    _LOGGER.info(f"{ragdoll_entry.name} ragdoll physics scaled by {scale_factor}.")

    try:
        cloth_entry = chrbnd.find_entry_matching_name(rf"{model_name}_c\.hkx")
    except ValueError:
        # No cloth data.
        _LOGGER.info("No cloth HKX found.")
    else:
        if cloth_entry.entry_id != 700:
            _LOGGER.warning(f"Cloth entry ID is {cloth_entry.entry_id}, not 700.")
        cloth_hkx = cloth_entry.to_game_file(ClothHKX)
        cloth_hkx.cloth_physics_data.scale_all_translations(scale_factor)
        cloth_entry.set_from_game_file(cloth_hkx)
        _LOGGER.info(f"{cloth_entry.name} cloth physics scaled by {scale_factor}.")

    _LOGGER.info("CHRBND scaling complete.")


def scale_anibnd(anibnd: Binder, scale_factor: float):
    """Scale skeleton and all animations in ANIBND in-place."""

    skeleton_entry = anibnd.find_entry_matching_name(r"[Ss]keleton\.(HKX|hkx)")
    if skeleton_entry.entry_id != 1000000:
        _LOGGER.warning(f"Skeleton entry ID is {skeleton_entry.entry_id}, not 1000000.")
    skeleton_hkx = skeleton_entry.to_game_file(SkeletonHKX)
    skeleton_hkx.skeleton.scale_all_translations(scale_factor)
    skeleton_entry.set_from_game_file(skeleton_hkx)
    _LOGGER.info(f"{skeleton_entry.name} skeleton scaled by {scale_factor}.")

    animation_entries = anibnd.find_entries_matching_name(r"a.*\.hkx")
    for entry in animation_entries:
        _LOGGER.info(f"  Scaling animation {entry.entry_id} by {scale_factor}...")
        animation_hkx = entry.to_game_file(AnimationHKX)  # "aXX_XXXX.hkx"
        animation_hkx.animation_container.scale_all_translations(scale_factor)
        entry.set_from_game_file(animation_hkx)

    _LOGGER.info("ANIBND scaling complete.")


def scale_objbnd(objbnd: Binder, scale_factor: float):
    """Scale FLVER and HKX models in OBJBND in-place."""
    try:
        flver_entry = objbnd.find_entry_matching_name(r".*\.flver")
    except BinderEntryNotFoundError:  # e.g. fog walls
        _LOGGER.info("No FLVER model found in OBJBND.")
    else:
        if flver_entry.entry_id != 200:
            _LOGGER.warning(f"FLVER entry ID is {flver_entry.entry_id}, not 200.")
        model = flver_entry.to_game_file(FLVER)
        model.scale_all_translations(scale_factor)
        flver_entry.set_from_game_file(model)
        _LOGGER.info(f"{flver_entry.name} model scaled by {scale_factor}.")

    try:
        collision_hkx_entry = objbnd.find_entry_matching_name(r".*\.hkx")
    except BinderEntryNotFoundError:  # many objects do not have collision
        _LOGGER.info("No HKX collision found in OBJBND.")
    else:
        if collision_hkx_entry.entry_id != 300:
            _LOGGER.warning(f"Collision entry ID is {collision_hkx_entry.entry_id}, not 300.")
        collision_hkx = collision_hkx_entry.to_game_file(CollisionHKX)
        collision_hkx.physics_data.scale_all_translations(scale_factor)
        collision_hkx_entry.set_from_game_file(collision_hkx)
        _LOGGER.info(f"{collision_hkx_entry.name} collision rigid bodies scaled by {scale_factor}.")

    _LOGGER.info("OBJBND scaling complete.")


def scale_character_files(chr_directory: Path | str, model_id: int, scale_factor: float, prefer_bak=False):
    """Find the `chrbnd` and `anibnd` binders for character `model_id` in `chr_directory`, scale them by `scale_factor`,
    and write them back to disk at the same locations.

    If `prefer_bak` is True, will use the `.bak` file if it exists.
    """
    if model_id == 0:
        # TODO: Cannot handle c0000.
        raise NotImplementedError("Cannot scale c0000 in DSR yet (appearance is composed of `partsbnd` models).")

    model_name = f"c{model_id:04d}"
    chrbnd_path = Path(chr_directory) / f"{model_name}.chrbnd.dcx"
    anibnd_path = Path(chr_directory) / f"{model_name}.anibnd.dcx"
    if not chrbnd_path.is_file():
        raise FileNotFoundError(f"Cannot find `chrbnd` file: '{chrbnd_path}'")
    if not anibnd_path.is_file():
        raise FileNotFoundError(f"Cannot find `anibnd` file: '{anibnd_path}'")

    chrbnd = Binder.from_bak(chrbnd_path) if prefer_bak else Binder.from_path(chrbnd_path)
    anibnd = Binder.from_bak(anibnd_path) if prefer_bak else Binder.from_path(anibnd_path)

    scale_chrbnd(chrbnd, scale_factor)
    scale_anibnd(anibnd, scale_factor)
    print("Writing `chrbnd` and `anibnd` (creating '.bak' backups if absent)...")
    chrbnd.write()
    anibnd.write()
    print(f"Character {model_name} files scaled by {scale_factor} and written successfully.")


def reverse_animation_in_anibnd_file(
    anibnd_path: Path | str, source_animation_id: int, new_animation_id: int = None, prefer_bak=True
):
    """Unpack given animation (HKX file) inside given ANIBND and reverse its frames."""
    anibnd_path = Path(anibnd_path)
    anibnd = Binder.from_bak(anibnd_path) if prefer_bak else Binder.from_path(anibnd_path)
    try:
        animation_entry = anibnd.entries_by_id[source_animation_id]
    except KeyError:
        raise KeyError(f"Could not find animation ID {source_animation_id} in '{anibnd_path.name}'.")
    animation = animation_entry.to_game_file(AnimationHKX)
    print(f"Reversing animation {source_animation_id}...")
    animation.animation_container.reverse()
    if new_animation_id is None or new_animation_id == source_animation_id:
        # In-place modification is complete.
        animation_entry.set_from_game_file(animation)
    else:
        if new_animation_id in anibnd.entries_by_id:
            raise KeyError(
                f"Animation ID {new_animation_id} already exists in `anibnd`. If you want to overwrite it with "
                f"reversed animation, do not provide `new_animation_id`."
            )
        new_entry_stem = get_animation_file_stem(new_animation_id)
        new_entry = animation_entry.copy()
        new_entry.entry_id = new_animation_id
        new_entry.path = str(Path(new_entry.path).parent / f"{new_entry_stem}.hkx")
        new_entry.set_from_game_file(animation)
        print(f"    Saving as new animation {new_animation_id}.")
    anibnd.write()
    print(f"Modified `anibnd` '{anibnd_path}' written successfully.")


def get_animation_file_stem(animation_id: int) -> str:
    """Animation HKX file stems are of the form `aXX_XXXX` in DS1."""
    # TODO: Don't c0000 animations go above 99999 in the split ANIBND files?
    if animation_id > 99999:
        raise ValueError(f"Invalid animation ID: {animation_id}. Must be <= 99999 in DSR.")
    return f"a{animation_id // 10000:02d}_{animation_id % 10000:04d}"
