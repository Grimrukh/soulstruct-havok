from soulstruct.utilities.inspection import compare_binary_files

from soulstruct_havok.core import HKX
from soulstruct_havok.types.debug import SET_DEBUG_PRINT


def bb_packfile_test():
    """Test HKX Packfile format (hk2014) with c2020 from Bloodborne."""
    SET_DEBUG_PRINT(unpack=False, pack=False)

    for file_name, display_name in (
        # ("a000_003000.hkx", "Attack 3000"),
        # ("skeleton.HKX", "Skeleton"),
        ("c2020.HKX", "Ragdoll"),
        # ("c2020_c.hkx", "Cloth"),
    ):
        print(f"Reading c2020 {display_name}...")
        c2020 = HKX.from_path(f"resources/BB/c2020/{file_name}")
        print(f"Writing c2020 {display_name}...")
        c2020.write(f"re_c2020_{file_name}")
        compare_binary_files(f"resources/BB/c2020/{file_name}", f"re_c2020_{file_name}")
        print(f"Re-reading c2020 {display_name}...")
        HKX.from_path(f"re_c2020_{file_name}")


def ds3_packfile_test():
    """Test HKX Packfile format with c1240 from Dark Souls III."""

    SET_DEBUG_PRINT(unpack=True, pack=False)

    print("Reading c1430 skeleton...")
    c1430_ragdoll = HKX.from_path("resources/DS3/c1430/skeleton.HKX")
    print("Writing c1430 skeleton...")
    c1430_ragdoll.write("re_c1430_skeleton.HKX")

    compare_binary_files("resources/DS3/c1430/skeleton.HKX", "re_c1430_skeleton.HKX")

    print("Re-reading c1430 skeleton...")
    re_c1430_skeleton = HKX.from_path("re_c1430_skeleton.HKX")

    print("Reading c1430 ragdoll...")
    c1430_ragdoll = HKX.from_path("resources/DS3/c1430/c1430.HKX")
    print("Writing c1430 ragdoll...")
    c1430_ragdoll.write("re_c1430.HKX")

    # Type entries not repacked, so these files differ massively.
    # compare_binary_files("resources/DS3/c1430/c1430.HKX", "re_c1430.HKX")

    print("Re-reading c1430 ragdoll...")
    re_c1430_ragdoll = HKX.from_path("re_c1430.HKX")

    print("Reading c1240 animation 3000...")
    a00_3000 = HKX.from_path("resources/DS3/c1240/a00_3000.hkx")
    print("Writing c1240 animation 3000...")
    a00_3000.write("re_a00_3000.hkx")

    compare_binary_files("resources/DS3/c1240/a00_3000.hkx", "re_a00_3000.hkx")

    print("Re-reading c1240 animation 3000...")
    re_a00_3000 = HKX.from_path("re_a00_3000.hkx")


def ptde_packfile_test():
    """Test HKX Packfile format with c2240 from Dark Souls: Prepare to Die Edition."""
    print("Reading Capra Demon animation 0...")
    capra_anim_0 = HKX.from_path("resources/PTDE/c2240/a00_0000.hkx")

    print("Reading Capra Demon animation 3000...")
    capra_anim_3000 = HKX.from_path("resources/PTDE/c2240/a00_3000.hkx")

    print("Reading Capra Demon skeleton...")
    capra_skeleton = HKX.from_path("resources/PTDE/c2240/Skeleton.HKX")

    print("Reading Capra Demon ragdoll...")
    capra_ragdoll = HKX.from_path("resources/PTDE/c2240/c2240.hkx")
    print(capra_ragdoll.get_root_tree_string())


if __name__ == '__main__':
    # ptde_packfile_test()
    # ds3_packfile_test()
    bb_packfile_test()
