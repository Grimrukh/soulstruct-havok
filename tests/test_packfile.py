import contextlib
from pathlib import Path

from soulstruct import DSR_PATH, PTDE_PATH, DS3_PATH, Binder

from soulstruct_havok.core import HKX
from soulstruct_havok.types.core import SET_DEBUG_PRINT


def ptde_c2500_test():
    c2500_anibnd_path = Path(PTDE_PATH + "/chr/c2500.anibnd")
    c2500_anibnd = Binder.from_path(c2500_anibnd_path)
    c2500_a00_0000 = c2500_anibnd[0].to_binary_file(HKX)


def ds3_c1430_test():

    # SET_DEBUG_PRINT(True, False)

    c1430_anibnd_path = Path(DS3_PATH + "/chr/c1430.anibnd_vanilla.dcx")
    c1430_anibnd = Binder.from_bak(c1430_anibnd_path)

    with contextlib.redirect_stdout(open("ds3_c1430_skeleton_unpack.txt", "w")):
        c1430_skeleton = c1430_anibnd[1000000].to_binary_file(HKX)
    print("Unpacked skeleton successfully.")
    Path("ds3_c1430_skeleton.hkx.txt").write_text(c1430_skeleton.get_root_tree_string())
    c1430_anibnd[1000000].set_from_binary_file(c1430_skeleton)
    print("    --> Repacked skeleton successfully.")

    c1430_chrbnd_path = Path(DS3_PATH + "/chr/c1430.chrbnd_vanilla.dcx")
    c1430_chrbnd = Binder.from_path(c1430_chrbnd_path)

    with contextlib.redirect_stdout(open("ds3_c1430_ragdoll_unpack.txt", "w")):
        c1430_ragdoll = c1430_chrbnd[300].to_binary_file(HKX)
    print("Unpacked ragdoll successfully.")
    Path("ds3_c1430_ragdoll.hkx.txt").write_text(c1430_ragdoll.get_root_tree_string())
    c1430_ragdoll.write("c1430.hkx")

    exit()

    with contextlib.redirect_stdout(open("ds3_c1430_ragdoll_repack_unpack.txt", "w")):
        c1430_ragdoll_repack = HKX.from_path("repack.hkx")
    Path("ds3_c1430_ragdoll_repack.hkx.txt").write_text(c1430_ragdoll_repack.get_root_tree_string())
    c1430_chrbnd[300].data = c1430_ragdoll.pack()
    print("    --> Repacked ragdoll successfully.")

    # TODO: I don't have 2014 `hcl` cloth classes yet.
    # c1430_cloth = HKX(c1430_chrbnd[700])
    # print("Unpacked cloth successfully.")

    c1430_anibnd.write(Path(DS3_PATH + "/chr/c1430.anibnd.dcx"))  # WORKS (but only has skeleton)
    c1430_chrbnd.write(Path(DS3_PATH + "/chr/c1430.chrbnd.dcx"))  # TODO: Ragdoll repack crashes.


def bb_cloth_test():
    c2310_c = HKX.from_path("resources/BB/c2310/c2310-chrbnd-dcx/chr/c2310/c2310_c.hkx")


def dsr_cloth_test():
    silver_knight_cloth = HKX.from_binder(DSR_PATH + "/chr/c2410.chrbnd.dcx", 700)
    print(silver_knight_cloth)


def packfile_test():
    """Test HKX Packfile format with c1240 from Dark Souls III."""

    SET_DEBUG_PRINT()
    # with open("DS3_c1240_a00_3000.hkx.unpack.txt", "w") as f:
    #     with contextlib.redirect_stdout(f):
    h = HKX.from_path("resources/DS3/c1240/a00_3000.hkx")

    print("Unpacked HKX successfully.")

    h.write("a00_3000_repack.hkx")

    print("Packed HKX successfully.")

    SET_DEBUG_PRINT(True, False)
    hh = HKX.from_path("a00_3000_repack.hkx")

    h_string = h.get_root_tree_string()
    Path("packfile.txt").write_text(h_string)
    hh_string = hh.get_root_tree_string()
    Path("packfile_repack.txt").write_text(hh_string)

    print("Unpacked repacked HKX successfully.")


def ptde_packfile_test():
    """Test HKX Packfile format with c2240 from Dark Souls: Prepare to Die Edition."""
    # print("Reading Capra Demon animation 0...")
    # capra_anim_0 = HKX.from_path("resources/PTDE/c2240/a00_0000.hkx")
    # print("Reading Capra Demon animation 3000...")
    # capra_anim_3000 = HKX.from_path("resources/PTDE/c2240/a00_3000.hkx")
    # print("Reading Capra Demon skeleton...")
    # capra_skeleton = HKX.from_path("resources/PTDE/c2240/Skeleton.HKX")
    print("Reading Capra Demon ragdoll...")
    capra_ragdoll = HKX.from_path("resources/PTDE/c2240/c2240.hkx")


if __name__ == '__main__':
    ptde_packfile_test()
