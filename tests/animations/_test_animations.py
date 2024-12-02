import time

from soulstruct import Path, ELDEN_RING_PATH
from soulstruct.eldenring.containers import DivBinder
from soulstruct_havok.types.debug import SET_DEBUG_PRINT
from soulstruct_havok.fromsoft import darksouls1ptde, darksouls1r, bloodborne, sekiro, eldenring


def test_ptde():
    path = Path("../resources/PTDE/c2240/a00_0200.hkx")
    SET_DEBUG_PRINT(True, dump_items=("hkaSplineCompressedAnimation",))
    hkx = darksouls1ptde.AnimationHKX.from_path(path)
    s1 = hkx.get_root_tree_string(max_primitive_sequence_size=10)

    hkx_interleaved = hkx.to_interleaved_hkx()
    spline_hkx = hkx_interleaved.to_spline_hkx()

    s2 = spline_hkx.get_root_tree_string(max_primitive_sequence_size=10)

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


def test_dsr():
    path = Path("../resources/DSR/c2240/a00_0000.hkx")
    # SET_DEBUG_PRINT(True, dump_items=("hkaSplineCompressedAnimation",))
    hkx = darksouls1r.AnimationHKX.from_path(path)

    hkx.animation_container.load_spline_data()
    s1 = hkx.get_root_tree_string(max_primitive_sequence_size=10)
    print(s1)

    p = time.perf_counter()
    hkx_scratch = darksouls1r.AnimationHKX.from_minimal_data_spline(
        spline_data=hkx.animation_container.spline_data,
        frame_count=hkx.animation_container.frame_count,
        transform_track_bone_indices=hkx.animation_container.get_track_bone_indices(),
        root_motion_array=hkx.animation_container.get_reference_frame_samples(),
        original_skeleton_name=hkx.animation_container.hkx_binding.originalSkeletonName,
        frame_rate=30.0,
        track_names=hkx.animation_container.get_track_annotation_names(),
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
    s1 = hkx.get_root_tree_string(max_primitive_sequence_size=10)

    hkx_interleaved = hkx.to_interleaved_hkx()
    spline_hkx = hkx_interleaved.to_spline_hkx()

    s2 = spline_hkx.get_root_tree_string(max_primitive_sequence_size=10)

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


def test_er():

    chrbnd_path = Path(ELDEN_RING_PATH, "../../ELDEN RING (Modding 1.12)/Game/chr/c3251.chrbnd.dcx")
    from soulstruct import FLVER
    flver = FLVER.from_binder_path(chrbnd_path, "c3251.flver")
    flver_bone_names = [bone.name for bone in flver.bones]

    div_path = Path("../resources/ER/c3251.anibnd.dcx")
    div_binder = DivBinder.from_path(div_path)
    # SET_DEBUG_PRINT(True, dump_items=("hkaSplineCompressedAnimation",))
    hkx = eldenring.AnimationHKX.from_binder(
        div_binder, entry_spec="a000_003000.hkx", compendium_name="c3251_div00.compendium"
    )
    hkx_skeleton = eldenring.SkeletonHKX.from_binder(
        div_binder, entry_spec="skeleton.hkx", compendium_name="c3251_div00.compendium"
    )
    for bone in hkx_skeleton.skeleton.bones:
        if bone.name not in flver_bone_names:
            print(bone.name)
    return
    print(hkx.animation_container.get_track_annotation_names())
    hkx_interleaved = hkx.to_interleaved_hkx()
    arma_frames = hkx_interleaved.animation_container.get_interleaved_data_in_armature_space(hkx_skeleton.skeleton)
    # s1 = hkx.get_root_tree_string(max_primitive_sequence_size=10)
    print(len(arma_frames))
    print(len(arma_frames[0]))
    return

    spline_hkx = hkx_interleaved.to_spline_hkx()
    s2 = spline_hkx.get_root_tree_string(max_primitive_sequence_size=10)

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


if __name__ == '__main__':
    # test_ptde()
    # test_dsr()
    # test_bb()
    test_er()
