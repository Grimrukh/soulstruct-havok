from pathlib import Path

from soulstruct import DSR_PATH
from soulstruct.containers import Binder
from soulstruct_havok.wrappers.hkx2015 import MapCollisionHKX


def main():
    p = Path(DSR_PATH) / "map/m10_01_00_00/h10_01_00_00.hkxbhd"
    b = Binder.from_path(p)
    c = b["h0029B1A10.hkx.dcx"].to_binary_file(MapCollisionHKX)

    print("Original HKX:")
    for mesh in c.map_collision_physics_data.get_extended_mesh_meshstorage():
        print(len(mesh.vertices), len(mesh.indices16) / 4)
        print(mesh.indices16[:32])

    print("Meshes:")
    meshes = c.to_meshes()
    for verts, faces in meshes:
        print(len(verts), len(faces))

    re_c = MapCollisionHKX.from_meshes(
        meshes, "h0029B1A10", material_indices=c.map_collision_physics_data.get_subpart_materials()
    )
    print("New HKX:")
    for mesh in re_c.map_collision_physics_data.get_extended_mesh_meshstorage():
        print(len(mesh.vertices), len(mesh.indices16) / 4)
        print(mesh.indices16[:32])


def check():
    p = Path("~/Documents/untitled.hkx").expanduser()
    c = MapCollisionHKX.from_path(p)
    print("\n\nBlender exported HKX:")
    for mesh in c.map_collision_physics_data.get_extended_mesh_meshstorage():
        print(len(mesh.vertices), len(mesh.indices16) / 4)
        print(mesh.indices16[:32])


if __name__ == '__main__':
    main()
    check()
