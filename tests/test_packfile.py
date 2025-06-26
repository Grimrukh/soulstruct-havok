from soulstruct.utilities.inspection import compare_binary_data, compare_binary_files

from soulstruct.havok.core import HKX
from soulstruct.havok.types.debug import SET_DEBUG_PRINT


def bb_packfile_test():
    """Test HKX Packfile format (hk2014) with c2020 from Bloodborne."""
    SET_DEBUG_PRINT(unpack=False, pack=False)

    for file_name, display_name in (
        ("a000_003000.hkx", "Attack 3000"),
        ("skeleton.HKX", "Skeleton"),
        ("c2020.HKX", "Ragdoll"),
        ("c2020_c.hkx", "Cloth"),
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
    SET_DEBUG_PRINT(unpack=False, pack=False)

    for file_name, display_name in (
        ("a00_3000.hkx", "Attack 3000"),
        # ("skeleton.HKX", "Skeleton"),  # works
        # ("c2240.hkx", "Ragdoll"),  # TODO: Write is failing on this one. But fixing animation read/write first.
        # ("c2240_c.hkx", "Cloth"),  # TODO: no cloth for Capra - try another model
    ):
        print(f"Reading c2240 {display_name}...")
        c2240 = HKX.from_path(f"resources/PTDE/c2240/{file_name}")
        print(f"  Writing c2240 {display_name}...")
        c2240.write(f"re_c2240_{file_name}")
        compare_binary_files(f"resources/PTDE/c2240/{file_name}", f"re_c2240_{file_name}")
        print(f"  Re-reading c2240 {display_name}...")
        HKX.from_path(f"re_c2240_{file_name}")
        print(f"  TEST SUCCESSFUL: {file_name}")


def dsr_spline_conversion_test():
    """Test conversion of 2015 spline animations to 2010 interleaved, and vice versa, with Hork's tool."""
    from soulstruct.havok.fromsoft.darksouls1r import AnimationHKX

    SET_DEBUG_PRINT(unpack=False, pack=False)

    anim_spline = AnimationHKX.from_path("resources/DSR/c2240/a00_0000.hkx")
    anim_interleaved = anim_spline.to_interleaved_hkx()
    anim_re_spline = anim_interleaved.to_spline_hkx()
    anim_re_spline.write("c2240_resplined_a00_0000.hkx")
    AnimationHKX.from_path("c2240_resplined_a00_0000.hkx")


if __name__ == '__main__':
    ptde_packfile_test()
    # ds3_packfile_test()
    # bb_packfile_test()
    # dsr_spline_conversion_test()

