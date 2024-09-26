from soulstruct_havok.core import HKX


def main():
    hkx_path = "resources/DSR/h0000B0A10.hkx.dcx"
    hkx = HKX.from_path(hkx_path)
    print(hkx.get_root_tree_string(max_primitive_sequence_size=10))


if __name__ == '__main__':
    main()
