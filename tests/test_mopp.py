from pathlib import Path

from soulstruct.containers import Binder
from soulstruct.containers.dcx import DCXType

from soulstruct_havok.hkx2015 import CollisionHKX


def mopp_test(map_name: str, col_name: str, write_mesh_obj=False, restore_bak_only=False):
    """Take a DSR mesh, changes its vertices, and generate new MOPP code."""
    if col_name[0] in "hl":
        raise ValueError("`col_name` should omit the h/l prefix, e.g., '0025B0'.")

    map_path = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/map")

    hi_hit = Binder(map_path / f"{map_name}/h{map_name[1:]}.hkxbhd", from_bak=True)
    lo_hit = Binder(map_path / f"{map_name}/l{map_name[1:]}.hkxbhd", from_bak=True)

    if restore_bak_only:
        hi_hit.write()
        lo_hit.write()
        print("# Restored bak HKX files.")
        return

    hi_col_entry = hi_hit.find_entry_matching_name("h" + col_name)
    hi_col_hkx = CollisionHKX(hi_col_entry)
    lo_col_entry = lo_hit.find_entry_matching_name("l" + col_name)
    lo_col_hkx = CollisionHKX(lo_col_entry)

    # print(hi_col_hkx.get_root_tree_string(max_primitive_sequence_size=16))
    # printf(lo_col_hkx.get_root_tree_string(max_primitive_sequence_size=200))

    if write_mesh_obj:
        hi_col_hkx.write_obj(f"{map_name}_h{col_name}.obj")
        lo_col_hkx.write_obj(f"{map_name}_l{col_name}.obj")

    for col in (hi_col_hkx, lo_col_hkx):
        col.regenerate_mopp_data()

    hi_col_entry.set_uncompressed_data(hi_col_hkx.pack_dcx())
    lo_col_entry.set_uncompressed_data(lo_col_hkx.pack_dcx())

    hi_hit.write()
    lo_hit.write()
    print("# New HKX files written successfully.")


def get_hkx_material_name_data(map_name: str, col_name: str) -> tuple[list[int], list[int]]:
    if col_name[0] in "hl":
        raise ValueError("`col_name` should omit the h/l prefix, e.g., '0025B0'.")

    map_path = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/map")

    hi_hit = Binder(map_path / f"{map_name}/h{map_name[1:]}.hkxbhd", from_bak=True)
    hi_col_entry = hi_hit.find_entry_matching_name("h" + col_name)
    hi_col_hkx = CollisionHKX(hi_col_entry)
    child_shape = hi_col_hkx.get_child_shape()
    hi_material_name_data = [material.materialNameData for material in child_shape.materialArray]

    lo_hit = Binder(map_path / f"{map_name}/l{map_name[1:]}.hkxbhd", from_bak=True)
    lo_col_entry = lo_hit.find_entry_matching_name("l" + col_name)
    lo_col_hkx = CollisionHKX(lo_col_entry)
    child_shape = lo_col_hkx.get_child_shape()
    lo_material_name_data = [material.materialNameData for material in child_shape.materialArray]

    return hi_material_name_data, lo_material_name_data


def set_hkx_material_name_data(
    map_name: str,
    col_name: str,
    hi_material_name_data: tuple[int, ...],
    lo_material_name_data: tuple[int, ...],
):
    """Load an HKX from the specified BXF and change its material name data."""
    if col_name[0] in "hl":
        raise ValueError("`col_name` should omit the h/l prefix, e.g., '0025B0'.")

    map_path = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/map")

    hi_hit = Binder(map_path / f"{map_name}/h{map_name[1:]}.hkxbhd", from_bak=True)
    hi_col_entry = hi_hit.find_entry_matching_name("h" + col_name)
    hi_col_hkx = CollisionHKX(hi_col_entry)
    child_shape = hi_col_hkx.get_child_shape()
    if len(child_shape.materialArray) != len(hi_material_name_data):
        raise ValueError(
            f"Hi-res material count ({len(child_shape.materialArray)}) "
            f"!= new material count ({len(hi_material_name_data)})."
        )
    for material, new_id in zip(child_shape.materialArray, hi_material_name_data):
        material.materialNameData = new_id

    lo_hit = Binder(map_path / f"{map_name}/l{map_name[1:]}.hkxbhd", from_bak=True)
    lo_col_entry = lo_hit.find_entry_matching_name("l" + col_name)
    lo_col_hkx = CollisionHKX(lo_col_entry)
    child_shape = lo_col_hkx.get_child_shape()
    if len(child_shape.materialArray) != len(lo_material_name_data):
        raise ValueError(
            f"Lo-res material count ({len(child_shape.materialArray)}) "
            f"!= new material count ({len(lo_material_name_data)})."
        )
    for material, new_id in zip(child_shape.materialArray, lo_material_name_data):
        material.materialNameData = new_id

    hi_col_entry.set_uncompressed_data(hi_col_hkx.pack_dcx())
    lo_col_entry.set_uncompressed_data(lo_col_hkx.pack_dcx())

    hi_hit.write()
    lo_hit.write()
    print("# New HKX files written successfully.")


def hkx_to_obj(map_name: str, col_name: str):
    if col_name[0] in "hl":
        raise ValueError("`col_name` should omit the h/l prefix, e.g., '0025B0'.")

    map_path = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/map")

    hi_hit = Binder(map_path / f"{map_name}/h{map_name[1:]}.hkxbhd", from_bak=True)
    hi_col_entry = hi_hit.find_entry_matching_name("h" + col_name)
    hi_col_hkx = CollisionHKX(hi_col_entry)
    hi_col_hkx.write_obj(f"{map_name}_h{col_name}.obj")

    lo_hit = Binder(map_path / f"{map_name}/l{map_name[1:]}.hkxbhd", from_bak=True)
    lo_col_entry = lo_hit.find_entry_matching_name("l" + col_name)
    lo_col_hkx = CollisionHKX(lo_col_entry)
    lo_col_hkx.write_obj(f"{map_name}_l{col_name}.obj")


def insert_obj_in_hkxbxf(
    map_name: str,
    col_name: str,
    hi_obj_path: Path | str = None,
    lo_obj_path: Path | str = None,
    hi_material_name_data=(),
    lo_material_name_data=(),
    dcx_type=DCXType.DCX_DFLT_10000_24_9,  # DS1 default
):
    if not (hi_obj_path or lo_obj_path):
        raise ValueError("Must give `hi` and/or `lo` OBJ path.")
    if col_name[0] in "hl":
        raise ValueError("`col_name` should omit the h/l prefix, e.g., '0025B0'.")

    map_path = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/map")

    if hi_obj_path:
        hi_hit = Binder(map_path / f"{map_name}/h{map_name[1:]}.hkxbhd", from_bak=True)
        hi_col_entry = hi_hit.find_entry_matching_name("h" + col_name)
        hi_col_hkx = CollisionHKX.from_obj(
            hi_obj_path,
            "h" + col_name,
            material_name_data=hi_material_name_data,
            template_hkx=CollisionHKX(hi_col_entry),
            dcx_type=dcx_type,  # should come from template
        )
        print(hi_col_hkx.get_root_tree_string(max_primitive_sequence_size=16))
        hi_col_entry.set_uncompressed_data(hi_col_hkx.pack_dcx())
        hi_hit.write()
        print("# New hi-res HKX (from OBJ) written successfully.")

    if lo_obj_path:
        lo_hit = Binder(map_path / f"{map_name}/l{map_name[1:]}.hkxbhd", from_bak=True)
        lo_col_entry = lo_hit.find_entry_matching_name("l" + col_name)
        lo_col_hkx = CollisionHKX.from_obj(
            lo_obj_path,
            "l" + col_name,
            material_name_data=lo_material_name_data,
            template_hkx=CollisionHKX(lo_col_entry),
            dcx_type=dcx_type,
        )
        print(lo_col_hkx.get_root_tree_string(max_primitive_sequence_size=16))
        lo_col_entry.set_uncompressed_data(lo_col_hkx.pack_dcx())
        lo_hit.write()
        print("# New lo-res HKX (from OBJ) written successfully.")


HKX_MATERIALS = {
    0: "?",  # just soft footstep sounds?
    1: "MetalWall",  # walls make clang sound when hit
    2: "?",  # just soft footstep sounds?
    7: "Snow",  # snow footstep VFX/SFX
    17: "Unknown",  # used at edges of snow ground
    204: "WoodWall",  # tree trunks
}


if __name__ == '__main__':
    # set_hkx_material_name_data(
    #     "m11_00_00_00",
    #     "0025B0",
    #     hi_material_name_data=(0, 0, 1, 9),  # [0, 0, 1, 9]
    #     lo_material_name_data=(7, 1, 9, 1, 17, 204),  # [7, 1, 9, 0, 17, 204]
    # )

    # hkx_to_obj(
    #     "m11_00_00_00",
    #     "0025B0",
    # )

    insert_obj_in_hkxbxf(
        "m11_00_00_00",
        "0025B0",
        hi_obj_path="m11_00_00_00_h0025B0_blender.obj",
        lo_obj_path="m11_00_00_00_l0025B0_blender.obj",
    )
