from soulstruct import Path, DSR_PATH
from soulstruct_havok import HKX
from soulstruct_havok.wrappers.hkx2015 import AnimationHKX


def main():
    anibnd_path = Path(DSR_PATH, "chr/c1200.anibnd.dcx")
    a00_3000 = AnimationHKX.from_binder_path(anibnd_path, "a00_3000.hkx")
    a00_3000.animation_container.spline_to_interleaved()

    # a00_3000.write("c1200_a00_3000_interleaved_old.hkx")
    # a00_3000_2010 = a00_3000.to_2010_hkx()
    # a00_3000_2010.write("c1200_a00_3000_interleaved_hk2010.hkx")

    print("Converted spline to interleaved.")
    a00_3000.get_spline_hkx()


def compare():
    from soulstruct.utilities.inspection import compare_binary_files
    compare_binary_files("c1200_a00_3000_interleaved_hk2010_old.hkx", "c1200_a00_3000_interleaved_hk2010.hkx")


if __name__ == '__main__':
    main()
    # compare()
