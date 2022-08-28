from pathlib import Path

from soulstruct.containers import Binder
from soulstruct.containers.dcx import DCXType

from soulstruct_havok.hkx2015 import CollisionHKX


def mopp_test(
    map_name: str,
    col_name: str,
    write_mesh_obj=False,
    restore_bak_only=False,
):
    """Take a DSR mesh, changes its vertices, and generate new MOPP code."""
    map_path = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/map")

    hi_hit = Binder(map_path / f"{map_name}/h{map_name[1:]}.hkxbhd", from_bak=True)
    lo_hit = Binder(map_path / f"{map_name}/l{map_name[1:]}.hkxbhd", from_bak=True)

    if restore_bak_only:
        hi_hit.write()
        lo_hit.write()
        print("# Restored bak HKX files.")
        return

    hi_col_entry = hi_hit.find_entry_matching_name(col_name)
    hi_col_hkx = CollisionHKX(hi_col_entry)
    lo_col_entry = lo_hit.find_entry_matching_name(f"l{col_name[1:]}")
    lo_col_hkx = CollisionHKX(lo_col_entry)

    # print(hi_col_hkx.get_root_tree_string(max_primitive_sequence_size=16))
    # printf(lo_col_hkx.get_root_tree_string(max_primitive_sequence_size=200))

    if write_mesh_obj:
        hi_col_hkx.write_obj(f"{map_name}_{col_name}.obj")
        lo_col_hkx.write_obj(f"{map_name}_l{col_name[1:]}.obj")

    for col in (hi_col_hkx, lo_col_hkx):
        col.regenerate_mopp_data()

    hi_col_entry.set_uncompressed_data(hi_col_hkx.pack_dcx())
    lo_col_entry.set_uncompressed_data(lo_col_hkx.pack_dcx())

    hi_hit.write()
    lo_hit.write()
    print("# New HKX files written successfully.")


def insert_obj_in_hkxbxf(
    map_name: str,
    col_name: str,
    obj_path: Path | str,
):
    map_path = Path("C:/Steam/steamapps/common/DARK SOULS REMASTERED (NF New)/map")

    hi_hit = Binder(map_path / f"{map_name}/h{map_name[1:]}.hkxbhd", from_bak=True)
    lo_hit = Binder(map_path / f"{map_name}/l{map_name[1:]}.hkxbhd", from_bak=True)

    hi_col_entry = hi_hit.find_entry_matching_name(col_name)
    hi_col_hkx = CollisionHKX.from_obj(obj_path, col_name)
    hi_col_hkx.dcx_type = DCXType.DCX_DFLT_10000_24_9

    lo_col_entry = lo_hit.find_entry_matching_name(f"l{col_name[1:]}")
    lo_col_hkx = CollisionHKX.from_obj(obj_path, f"l{col_name[1:]}")
    lo_col_hkx.dcx_type = DCXType.DCX_DFLT_10000_24_9

    hi_col_entry.set_uncompressed_data(hi_col_hkx.pack_dcx())
    lo_col_entry.set_uncompressed_data(lo_col_hkx.pack_dcx())

    hi_hit.write()
    lo_hit.write()
    print("# New HKX files (from OBJ) written successfully.")


if __name__ == '__main__':
    mopp_test(
        "m11_00_00_00",
        "h0025B0",
        write_mesh_obj=True,
        restore_bak_only=False,
    )
    # insert_obj_in_hkxbxf(
    #     "m11_00_00_00",
    #     "h0025B0",
    #     obj_path="m11_00_00_00_h0025B0_blender.obj",
    # )
