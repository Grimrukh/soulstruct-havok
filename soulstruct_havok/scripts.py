import typing as tp
from pathlib import Path

from soulstruct.base.models.flver import FLVER
from soulstruct.containers.bnd import BND3

from soulstruct_havok.wrappers.hkx2015 import AnimationHKX, ClothHKX, RagdollHKX, SkeletonHKX


def scale_dsr_character(dsr_chr_path: tp.Union[str, Path], model_id: int, scale_factor: float, prefer_bak=False):
    """Scale the given `model_id` character by finding and modifying CHRBND and ANIBND HKX data in `dsr_chr_path`."""
    if model_id == 0:
        # TODO: Cannot handle c0000.
        raise NotImplementedError("Cannot scale c0000 in DSR yet.")
    model_name = f"c{model_id:04d}"
    chrbnd_path = Path(dsr_chr_path) / f"{model_name}.chrbnd.dcx"
    anibnd_path = Path(dsr_chr_path) / f"{model_name}.anibnd.dcx"
    if not chrbnd_path.is_file():
        raise FileNotFoundError(f"Cannot find CHRBND file: '{chrbnd_path}'")
    if not anibnd_path.is_file():
        raise FileNotFoundError(f"Cannot find ANIBND file: '{anibnd_path}'")

    chrbnd = BND3(chrbnd_path, from_bak=prefer_bak)
    anibnd = BND3(anibnd_path, from_bak=prefer_bak)
    print(f"Scaling {model_name} FLVER model...")
    flver = FLVER(chrbnd[200])
    flver.scale(scale_factor)
    chrbnd[200].data = flver.pack()
    print("    Done.")
    print(f"Scaling {model_name} ragdoll...")
    ragdoll = RagdollHKX(chrbnd[300])
    ragdoll.scale(scale_factor)
    chrbnd[300].data = ragdoll.pack()
    print("    Done.")
    print(f"Scaling {model_name} skeleton...")
    skeleton = SkeletonHKX(anibnd[1000000])
    skeleton.scale(scale_factor)
    anibnd[1000000].data = skeleton.pack()
    print("    Done.")
    try:
        cloth_file = chrbnd[f"{model_name}_c.hkx"]
    except KeyError:
        # No cloth for this character.
        print(f"No cloth file for {model_name}.")
    else:
        cloth = ClothHKX(cloth_file)
        print(f"Scaling {model_name} cloth...")
        cloth.scale(scale_factor)
        print("    Done.")
        chrbnd[f"{model_name}_c.hkx"].data = cloth.pack()
    print(f"Scaling {model_name} animations...")
    for entry_id, entry in anibnd.entries_by_id.items():
        if entry_id < 1000000:
            print(f"    Animation {entry_id}...")
            animation = AnimationHKX(entry)
            animation.scale(scale_factor)
            entry.data = animation.pack()
    print("    Done.")
    print("Writing CHRBND and ANIBND (creating '.bak' backups if absent)...")
    chrbnd.write()
    anibnd.write()
    print("    Done.")
    print(f"Character {model_name} scaling complete.")


def reverse_animation(
    anibnd_path: tp.Union[str, Path], animation_id: int, new_animation_id: int = None, prefer_bak=True
):
    """Unpack given animation (HKX file) inside given ANIBND and reverse its frames."""
    anibnd_path = Path(anibnd_path)
    anibnd = BND3(anibnd_path, from_bak=prefer_bak)
    try:
        animation_entry = anibnd.entries_by_id[animation_id]
    except KeyError:
        raise KeyError(f"No such animation in '{anibnd_path.name}': {animation_id}")
    animation = AnimationHKX(animation_entry)
    print(f"Reversing animation {animation_id}...")
    animation.reverse()
    if new_animation_id is None or new_animation_id == animation_id:
        animation_entry.data = animation.pack()
    else:
        if new_animation_id > 9999:
            raise ValueError(f"Invalid animation ID: {new_animation_id}. Must be <= 9999.")
        if new_animation_id in anibnd.entries_by_id:
            raise KeyError(f"Animation ID {new_animation_id} already exists in ANIBND.")
        new_entry = animation_entry.copy()
        new_entry.id = new_animation_id
        new_entry.path = str(Path(new_entry.path).parent / f"a00_{new_animation_id:04d}.hkx")
        new_entry.data = animation.pack()
        print(f"    Saving as new animation {new_animation_id}.")
    print("    Done.")
    anibnd.write()
    print(f"New ANIBND written: {anibnd_path}.")
