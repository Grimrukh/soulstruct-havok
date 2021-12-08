from pathlib import Path

from soulstruct.base.models.flver import FLVER
from soulstruct.config import DSR_PATH
from soulstruct.containers import Binder

from soulstruct_havok.core import HKX, AnimationHKX, SkeletonHKX, RagdollHKX, ClothHKX

GAME_CHR_PATH = Path(r"G:\Steam\steamapps\common\DARK SOULS REMASTERED\chr")


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


def print_cloth_physics():

    hkx = ClothHKX(Path("resources/DSR/c2410/c2410_c.hkx"))
    print(hkx.get_root_tree_string())


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


def load_collision():
    """
    TODO:
        - Collision loads fine, which is good.
        - There are vertices (obviously), `indices16` in the mesh (faces?), and `vertexDataBuffer` (same number as
        vertices) in the `materialArray` of the mesh, which probably indexes into the large `data` field of the
        `code` (`hkpMoppCode`) of the mesh. The size of `data` is not divisible by the number of vertices (it's about
        ~8.5 times as large). Of course, it could be some kind of compressed vertex data.


    """

    dsr_hkx = HKX("resources/h0001B0A10_DSR.hkx.dcx", hk_format="tagfile")
    print(dsr_hkx.get_root_tree_string())

    # mopp_code_data = dsr_hkx.get_variant_node(0)["systems"][0]["rigidBodies"][0]["collidable"]["shape"]["code"]["data"]
    # from soulstruct.utilities.inspection import get_hex_repr
    # print(get_hex_repr(bytearray(mopp_code_data)))

    # ptde_hkx = HKX("resources/h0001B0A10_PTDE.hkx", hkx_format="packfile")
    # print(ptde_hkx.get_root_tree_string())


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
    # TODO: Finally have a good-looking pack. Let's see if I fucked up the types...
    #  - Test repack works in game (c2240).
    #  - Generate 2014 classes from XML.
    #  - Update packfile unpacker. Fortunately, don't need writes.
    #  - Start actually fucking inspecting the hkp vs. hknp. Probably find out it's not possible. :/
    #       - In all seriousness, it HAS to be possible, even if I use a DSR model as a kind of template.

    import contextlib

    with open("real.txt", "w") as f:
        with contextlib.redirect_stdout(f):
            h = HKX("resources/DSR/c2240/c2240.hkx")
    # all_types = list(h.root.collect_types())
    # for t in set(all_types):
    #     print(t.__name__)

    # print(h.root["namedVariants"][0]["variant"])

    h.write("c2240_repack.hkx")

    with open("reopen.txt", "w") as f:
        with contextlib.redirect_stdout(f):
            hh = HKX("c2240_repack.hkx")


# noinspection PyTypeChecker,PyUnresolvedReferences
def packfile_test():
    import contextlib
    from soulstruct_havok.types import hk2015

    # with open("c2240_a00_3000.txt", "w") as f:
    #     with contextlib.redirect_stdout(f):
    #         h = HKX("resources/DSR/c2240/a00_3000.hkx")
    #         print(h.root.get_tree_string())

    with open("c2240.txt", "w") as f:
        with contextlib.redirect_stdout(f):
            h = HKX("resources/DSR/c2240/c2240.hkx")
            # print(h.root.get_tree_string())

    print("Original file unpacked.")

    h.write("c2240_repack.hkx")
    print("Original file repacked.")

    with open("c2240_repack.txt", "w") as f:
        with contextlib.redirect_stdout(f):
            h = HKX("c2240_repack.hkx")
            # print(h.root.get_tree_string())

    print("Repacked file unpacked again.")

    #     hkaAnimationContainer = h.root.namedVariants[0].variant
    #     hkaAnimationContainer: hk2015.hkaAnimationContainer
    #     for skeleton in hkaAnimationContainer.skeletons:
    #         print(
    #             f"Skeleton {skeleton.name} has {len(skeleton.bones)} bones "
    #             f"(reference pose len = {len(skeleton.referencePose)})."
    #         )
    #
    #     hkpPhysicsData = h.root.namedVariants[1].variant
    #     hkpPhysicsData: hk2015.hkpPhysicsData
    #     hkpPhysicsSystem = hkpPhysicsData.systems[0]
    #     print(f"Physics system has {len(hkpPhysicsSystem.rigidBodies)} rigid bodies.")

    # with open("c2800.txt", "w") as f:
    #     with contextlib.redirect_stdout(f):
    #         h = HKX("resources/BB/c2800/c2800.HKX")
    #         print(h.root.get_tree_string())
    #
    #     hkaAnimationContainer = h.root.namedVariants[0].variant
    #     hkaAnimationContainer: hk2014.hkaAnimationContainer
    #     for skeleton in hkaAnimationContainer.skeletons:
    #         print(
    #             f"Skeleton {skeleton.name} has {len(skeleton.bones)} bones "
    #             f"(reference pose len = {len(skeleton.referencePose)})."
    #         )
    #
    #     physics_data = h.root.namedVariants[1].variant
    #     physics_data: hk2014.hknpPhysicsSceneData
    #     physics_system = physics_data.systemDatas[0]
    #     print(f"Physics system has {len(physics_system.bodyCinfos)} body C infos (rigidbodies).")


if __name__ == '__main__':
    packfile_test()
