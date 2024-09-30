from soulstruct import Path, DSR_PATH
from soulstruct_havok import HKX
from soulstruct_havok.wrappers.hkx2015 import AnimationHKX


def main():
    path = Path("__temp_interleaved__.hkx")
    hkx = HKX.from_path(path)
    hkx.root.namedVariants[0].variant.bindings[0].animation = hkx.root.namedVariants[0].variant.animations[0]
    hkx.write("__fixed_interleaved__.hkx")
    # print(hkx.get_root_tree_string())


def main2():
    anibnd_path = Path(DSR_PATH, "chr/c1200.anibnd.dcx")
    a00_3000 = AnimationHKX.from_binder_path(anibnd_path, "a00_3000.hkx")
    a00_3000.animation_container.spline_to_interleaved()

    a00_3000.write("c1200_a00_3000_interleaved.hkx")

    # print("Converted spline to interleaved.")
    # a00_3000.get_spline_hkx()


if __name__ == '__main__':
    main2()
