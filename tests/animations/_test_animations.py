import time

from soulstruct import Path
from soulstruct_havok.types.debug import SET_DEBUG_PRINT
from soulstruct_havok.fromsoft import darksouls1ptde, darksouls1r, bloodborne, sekiro, eldenring


def test_ptde():
    path = Path("../resources/PTDE/c2240/a00_0200.hkx")
    SET_DEBUG_PRINT(True, dump_items=("hkaSplineCompressedAnimation",))
    hkx = darksouls1ptde.AnimationHKX.from_path(path)
    print(hkx.get_root_tree_string(max_primitive_sequence_size=10))


def test_dsr():
    path = Path("../resources/DSR/c2240/a00_0000.hkx")
    # SET_DEBUG_PRINT(True, dump_items=("hkaSplineCompressedAnimation",))
    hkx = darksouls1r.AnimationHKX.from_path(path)

    p = time.perf_counter()
    # hkx.animation_container.spline_to_interleaved()
    # print(f"Spline to interleaved conversion time: {time.perf_counter() - p:.4f}")
    hkx.animation_container.load_spline_data()
    s1 = hkx.get_root_tree_string(max_primitive_sequence_size=10)
    print(s1)

    p = time.perf_counter()
    hkx_scratch = darksouls1r.AnimationHKX.from_minimal_data_spline(
        spline_data=hkx.animation_container.spline_data,
        track_names=hkx.animation_container.get_track_names(),
        frame_count=hkx.animation_container.frame_count,
        transform_track_bone_indices=hkx.animation_container.get_track_bone_indices(),
        root_motion_array=hkx.animation_container.get_reference_frame_samples(),
        original_skeleton_name=hkx.animation_container.animation_binding.originalSkeletonName,
        frame_rate=30.0,
    )
    print(f"Scratch time: {time.perf_counter() - p:.4f}")

    p = time.perf_counter()
    s2 = hkx_scratch.get_root_tree_string(max_primitive_sequence_size=10)
    print(f"Scratch string time: {time.perf_counter() - p:.4f}")

    print(f"Equal? {s1 == s2}")

    # Print differences in strings, line by line.
    lines1 = s1.split("\n")
    lines2 = s2.split("\n")
    for i, (line1, line2) in enumerate(zip(lines1, lines2)):
        if line1 != line2:
            print(f"Line {i}:")
            print(f"  {line1}")
            print(f"  {line2}")
            print()


def test_bb():
    path = Path("../resources/BB/c2020/a000_003000.hkx")
    SET_DEBUG_PRINT(True, dump_items=("hkaSplineCompressedAnimation",))
    hkx = bloodborne.AnimationHKX.from_path(path)
    print(hkx.get_root_tree_string(max_primitive_sequence_size=10))


if __name__ == '__main__':
    # test_ptde()
    test_dsr()
    # test_bb()
