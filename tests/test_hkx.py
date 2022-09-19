from pathlib import Path

from soulstruct.base.models.flver import FLVER
from soulstruct.config import DSR_PATH
from soulstruct.containers import Binder

from soulstruct_havok.core import HKX
from soulstruct_havok.hkx2015 import AnimationHKX, RagdollHKX, SkeletonHKX, ClothHKX

GAME_CHR_PATH = DSR_PATH + "/chr"


def scale_character(model_name: str, scale_factor: float):
    chrbnd = Binder(GAME_CHR_PATH / f"{model_name}.chrbnd.dcx", from_bak=True)
    anibnd = Binder(GAME_CHR_PATH / f"{model_name}.anibnd.dcx", from_bak=True)

    model = FLVER(chrbnd[f"{model_name}.flver"])  # ID 200
    model.scale(scale_factor)
    chrbnd[f"{model_name}.flver"].set_uncompressed_data(model.pack())
    print("Model (FLVER) scaled.")

    ragdoll_hkx = RagdollHKX(chrbnd[f"{model_name}.hkx"])  # ID 300
    ragdoll_hkx.scale(scale_factor)
    chrbnd[f"{model_name}.hkx"].set_uncompressed_data(ragdoll_hkx.pack())
    print("Ragdoll physics scaled.")

    skeleton_hkx = SkeletonHKX(anibnd[1000000])   # "Skeleton.HKX" or "Skeleton.hkx"
    skeleton_hkx.scale(scale_factor)
    anibnd[1000000].set_uncompressed_data(skeleton_hkx.pack())
    print("Skeleton scaled.")

    try:
        cloth_entry = chrbnd[700]
    except KeyError:
        # No cloth data.
        print("No cloth HKX found.")
    else:
        cloth_hkx = ClothHKX(cloth_entry)
        print(cloth_hkx.get_root_tree_string())
        cloth_hkx.scale(scale_factor)
        print(cloth_hkx.get_root_tree_string())
        cloth_entry.set_uncompressed_data(cloth_hkx.pack())
        print("Cloth physics scaled.")

    print("Scaling animations:")
    for entry_id, entry in anibnd.entries_by_id.items():
        if entry_id < 1000000:
            print(f"  Scaling animation {entry_id}... ", end="")
            animation_hkx = AnimationHKX(entry)  # "aXX_XXXX.hkx"
            animation_hkx.scale(scale_factor)
            entry.set_uncompressed_data(animation_hkx.pack())
            print("Done.")

    print("Writing BNDs...")
    chrbnd.write()
    anibnd.write()
    print("Scaling complete.")


def retarget():
    """Challenges:

    - Scaling will be easy, but figuring out the bone mapping is harder.

    - Firstly, I need the ability to just remove tracks from the spline animation data without fully repacking it.
    Shouldn't be too hard using the same method as by scaling trick: unpack the data, keeping a separate writer, and
    only copy the data into the writer if it isn't one of the `excluded` track indices.

    - How do I handle missing bones in the dest model? That's fairly easy - just remove those tracks from the animation
    and ensure the rest are bound to the correct bones (as the indices of shared bones may change). This mapping can
    probably be handled by just looking up the index of the bone with the same name in the dest model (ignoring case).

    - How do I handle EXTRA bones in the dest model? That's a much harder issue, since the data for animating those
    bones just isn't there, yet those bones need to do something. It's POSSIBLE that Havok will just interpolate the
    movement of any bones that don't have a track in the animation. That's worth testing out. I don't really have any
    other option right now, since generating a new track would require new spline compression. We'll see what happens.

    - Anyway, for testing, we want two models with skeletons as similar as possible. Any differences should err toward
    less bones in the destination model. This is trickier than it sounds because a lot of humanoids have "cloth bones"
    that can vary a lot.
    """

    MODEL_1 = "c4100"
    MODEL_2 = "c2240"

    skeleton_1 = SkeletonHKX.from_anibnd(GAME_CHR_PATH / f"{MODEL_1}.anibnd.dcx", prefer_bak=True)
    print(f"{len(skeleton_1.skeleton.bones)} bones:")
    for bone, pose in zip(skeleton_1.skeleton.bones, skeleton_1.skeleton.reference_pose):
        print(f"    {bone.name}")
        # print("  ", pose.translation)

    print()
    skeleton_2 = SkeletonHKX.from_anibnd(GAME_CHR_PATH / f"{MODEL_2}.anibnd.dcx", prefer_bak=True)
    print(f"{len(skeleton_2.skeleton.bones)} bones:")
    for bone, pose in zip(skeleton_2.skeleton.bones, skeleton_2.skeleton.reference_pose):
        print(f"    {bone.name}")
        # print("  ", pose.translation)

    model_1_3000 = AnimationHKX.from_anibnd(GAME_CHR_PATH / f"{MODEL_1}.anibnd.dcx", 3000, prefer_bak=True)
    print(model_1_3000.animation_binding.transform_track_to_bone_indices)

    model_2_3000 = AnimationHKX.from_anibnd(GAME_CHR_PATH / f"{MODEL_2}.anibnd.dcx", 3000, prefer_bak=True)
    print(model_2_3000.animation_binding.transform_track_to_bone_indices)


def bb_to_dsr():
    """Try loading and converting c2800's ragdoll and an attack animation (3000) to DSR format."""
    # skeleton_hkx = HKX("resources/BB/c2800/Skeleton.HKX")
    # print("Skeleton loaded successfully.")
    # print(skeleton_hkx.root.get_tree_string(skeleton_hkx.hkx_types))

    ragdoll_hkx = HKX("resources/BB/c2020/c2020.HKX")
    print("Ragdoll loaded successfully.")
    # print(ragdoll_hkx.root.get_tree_string(ragdoll_hkx.hkx_types))
    # with open("bb_ragdoll.txt", "w") as f:
    #     f.write(ragdoll_hkx.root.get_tree_string(ragdoll_hkx.hkx_types))

    # capra_ragdoll = HKX("resources/DSR/c2240/c2240.hkx")
    # with open("dsr_ragdoll.txt", "w") as f:
    #     f.write(capra_ragdoll.root.get_tree_string(capra_ragdoll.hkx_types))
    # animation_hkx = HKX("resources/BB/c2800/a000_003000.hkx")
    # print("Animation loaded successfully.")
    # print(animation_hkx.root.get_tree_string(animation_hkx.hkx_types))


def new_tag_unpacker():
    h = HKX("resources/DSR/c2240/c2240.hkx")  # ragdoll
    print("Opened tagfile c2240 ragdoll successfully.")
    h_string = h.get_root_tree_string()

    print("Bones:")
    for bone in h.root.namedVariants[0].variant.skeletons[1].bones:
        print("   ", bone.name)
    print(f"Physics rigid bodies: {len(h.root.namedVariants[1].variant.systems[0].rigidBodies)}")
    print(f"Physics constraints: {len(h.root.namedVariants[1].variant.systems[0].constraints)}")
    for c in h.root.namedVariants[1].variant.systems[0].constraints:
        print("   ", c.name)
    print(f"Ragdoll rigid bodies: {len(h.root.namedVariants[2].variant.rigidBodies)}")
    for r in h.root.namedVariants[2].variant.rigidBodies:
        print("   ", r.name)
    print(f"Ragdoll constraints: {len(h.root.namedVariants[2].variant.constraints)}")
    for c in h.root.namedVariants[2].variant.constraints:
        print("   ", c.name)
    exit()

    h.write("c2240_repack.hkx")
    print("Wrote tagfile c2240 ragdoll successfully.")

    hh = HKX("c2240_repack.hkx")
    print("Re-opened tagfile c2240 ragdoll successfully.")
    hh_string = hh.get_root_tree_string()

    if h_string == hh_string:
        print("Re-opened file has identical tree string to original opened file.")
    else:
        print("ERROR: Re-opened file does NOT have identical tree string to original opened file.")

    # Inject into live c2240 CHRBND.
    chrbnd_path = GAME_CHR_PATH + "/c2240.chrbnd.dcx"
    chrbnd = Binder(chrbnd_path)
    chrbnd[300].set_uncompressed_data(h.pack())
    chrbnd.write()
    print("Wrote c2240 skeleton to game CHRBND.")

    Path("c2240.txt").write_text(h_string)
    Path("c2240_repack.txt").write_text(hh_string)


def er_test():
    chr_dir = Path("C:/Steam/steamapps/common/ELDEN RING (Vanilla)/Game/chr")
    anibnd = Binder(chr_dir / "c4810.anibnd.dcx")
    print(anibnd)
    compendium = HKX(anibnd["c4810.compendium"])
    skeleton = HKX(anibnd["skeleton.hkx"], compendium=compendium)
    print(skeleton.get_root_tree_string())


if __name__ == '__main__':
    # new_tag_unpacker()
    er_test()
