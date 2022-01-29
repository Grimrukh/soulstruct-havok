import contextlib
from pathlib import Path

from soulstruct import DSR_PATH, PTDE_PATH, DS3_PATH, Binder

from soulstruct_havok.core import HKX
from soulstruct_havok.types.core import SET_DEBUG_PRINT


def ptde_c2500_test():
    c2500_anibnd_path = Path(PTDE_PATH + "/chr/c2500.anibnd")
    c2500_anibnd = Binder(c2500_anibnd_path)
    c2500_a00_0000 = HKX(c2500_anibnd[0])


def ds3_c1430_test():

    # c1430_anibnd_path = Path(DS3_PATH + "/chr/c1430.anibnd_vanilla.dcx")
    # c1430_anibnd = Binder(c1430_anibnd_path, from_bak=True)
    # c1430_skeleton = HKX(c1430_anibnd[1000000])
    # c1430_anibnd[1000000].data = c1430_skeleton.pack()
    # c1430_anibnd.write(Path(DS3_PATH + "/chr/c1430.anibnd.dcx"))  # WORKS

    c1430_chrbnd_path = Path(DS3_PATH + "/chr/c1430.chrbnd_vanilla.dcx")
    c1430_chrbnd = Binder(c1430_chrbnd_path)
    c1430_ragdoll = HKX(c1430_chrbnd[300])
    print("Unpacked ragdoll successfully.")
    c1430_cloth = HKX(c1430_chrbnd[700])
    print("Unpacked cloth successfully.")


def bb_cloth_test():
    c2310_c = HKX("resources/BB/c2310/c2310-chrbnd-dcx/chr/c2310/c2310_c.hkx")


def dsr_cloth_test():
    silver_knight_cloth = HKX.from_binder(DSR_PATH + "/chr/c2410.chrbnd.dcx", 700)
    print(silver_knight_cloth)


def packfile_test():

    SET_DEBUG_PRINT()
    # with open("DS3_c1240_a00_3000.hkx.unpack.txt", "w") as f:
    #     with contextlib.redirect_stdout(f):
    h = HKX("resources/DS3/c1240/a00_3000.hkx")

    print("Unpacked HKX successfully.")

    h.write("a00_3000_repack.hkx")

    print("Packed HKX successfully.")

    SET_DEBUG_PRINT(True, False)
    hh = HKX("a00_3000_repack.hkx")

    h_string = h.get_root_tree_string()
    Path("packfile.txt").write_text(h_string)
    hh_string = hh.get_root_tree_string()
    Path("packfile_repack.txt").write_text(hh_string)

    print("Unpacked repacked HKX successfully.")


if __name__ == '__main__':
    # ds3_c1430_test()
    # bb_cloth_test()
    dsr_cloth_test()
