from soulstruct import Path, DSR_PATH
from soulstruct_havok import HKX
from soulstruct_havok.fromsoft.darksouls1r import AnimationHKX


def main():
    anibnd_path = Path(DSR_PATH, "chr/c2240.anibnd.dcx")
    a00_3000 = AnimationHKX.from_binder_path(anibnd_path, "a00_3000.hkx")

    print(a00_3000.get_root_tree_string(max_primitive_sequence_size=10))
    return


def compare():
    from soulstruct.utilities.inspection import compare_binary_files
    compare_binary_files("c1200_a00_3000_interleaved_hk2010_old.hkx", "c1200_a00_3000_interleaved_hk2010.hkx")


if __name__ == '__main__':
    main()
    # compare()
