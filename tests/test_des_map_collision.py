import numpy as np
from soulstruct_havok import HKX
from soulstruct_havok.wrappers.shared.map_collision import MapCollisionModel
from soulstruct_havok.types.debug import SET_DEBUG_PRINT


def test():
    SET_DEBUG_PRINT(True)
    hkx = HKX.from_path("resources/DES/h0004b0.hkx")
    # print(hkx.get_root_tree_string(max_primitive_sequence_size=5000))

    # model = MapCollisionModel.from_hkx(hkx)
    # SET_DEBUG_PRINT(False)

    # re_hkx = model.to_hkx()

    hkx.write("_test_hkx.hkx")
    re_re_hkx = HKX.from_path("_test_hkx.hkx")
    # print(re_re_hkx.get_root_tree_string(max_primitive_sequence_size=5000))


if __name__ == '__main__':
    test()
