from soulstruct.utilities.inspection import compare_binary_files

from soulstruct.havok.core import HKX
from soulstruct.havok.types.debug import SET_DEBUG_PRINT


def dsr_tagfile_test():
    """Test HKX Tagfile format (hk2015) with c2240 from DSR."""
    SET_DEBUG_PRINT(unpack=False, pack=False)

    for file_name, display_name in (
        ("a00_3000.hkx", "Attack 3000"),
        ("skeleton.HKX", "Skeleton"),
        ("c2240.hkx", "Ragdoll"),        
    ):
        print(f"Reading c2240 {display_name}...")
        c2240 = HKX.from_path(f"resources/DSR/c2240/{file_name}")
        print(f"Writing c2240 {display_name}...")
        c2240.write(f"re_c2240_{file_name}")
        compare_binary_files(f"resources/DSR/c2240/{file_name}", f"re_c2240_{file_name}")
        print(f"Re-reading c2240 {display_name}...")
        HKX.from_path(f"re_c2240_{file_name}")


# TODO: ER tagfile test.


if __name__ == '__main__':
    dsr_tagfile_test()
