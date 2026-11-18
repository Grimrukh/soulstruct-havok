import struct

import numpy as np
import pytest
from soulstruct.dcx import DCXType, compress

from soulstruct.havok.fromsoft.bloodborne import read_navmesh_geometry


def _packfile(data, fixups):
    """Wrap a synthetic hkaiNavMesh in the PS4 packfile sections."""
    names = struct.pack("<IB", 0, 9) + b"hkaiNavMesh\0"
    names += b"\xff"  # Some retail class-name tables have just one byte of padding.
    children = b"".join(struct.pack("<2I", *fixup) for fixup in fixups)
    spec = struct.pack("<3I", 0, 0, 5)

    header = bytearray(0x50)
    struct.pack_into("<4I4B4I", header, 0, 0x57E0E057, 0x10C0C010, 0, 11, 8, 1, 1, 1, 3, 2, 0, 0)
    header[0x28:0x36] = b"hk_2014.1.0-r1"
    header[0x37] = 0xFF
    struct.pack_into("<h", header, 0x3E, 16)

    def section(tag, base, offsets):
        return struct.pack("<19sB7I", tag, 0xFF, base, *offsets) + b"\xff" * 16

    names_start = len(header) + 3 * 64
    data_start = names_start + len(names)
    item_start = len(data) + len(children)
    end = item_start + len(spec)
    return bytes(
        header
        + section(b"__classnames__", names_start, [len(names)] * 6)
        + section(b"__types__", data_start, [0] * 6)
        + section(b"__data__", data_start, [len(data), item_start, item_start, end, end, end])
        + names
        + data
        + children
        + spec
    )


def _navmesh(*, empty=False, first_edge=0, last_edge_end=1):
    if empty:
        return _packfile(bytearray(64), [])
    faces_start = 64
    edges_start = faces_start + 32
    vertices_start = edges_start + 7 * 20
    data = bytearray(vertices_start + 6 * 16)
    arrays = [(16, faces_start, 2), (32, edges_start, 7), (48, vertices_start, 6)]
    for field, _, count in arrays:
        struct.pack_into("<I", data, field + 8, count)
    struct.pack_into("<i4xh", data, faces_start, first_edge, 4)
    struct.pack_into("<i4xh", data, faces_start + 16, 4, 3)
    for i, (a, b) in enumerate([(0, 2), (2, 3), (3, 4), (4, 0), (2, 5), (5, 3), (3, last_edge_end)]):
        struct.pack_into("<2I", data, edges_start + i * 20, a, b)
    for i, xyz in enumerate([(0, 3, 0), (99, 99, 99), (1, 3, 0), (1, 3, 1), (0, 3, 1), (2, 3, 1)]):
        struct.pack_into("<4f", data, vertices_start + i * 16, *xyz, 0.0)
    return _packfile(data, [(field, ptr) for field, ptr, _ in arrays])


def test_triangulates_directed_faces_and_compacts_unused_vertices(tmp_path):
    path = tmp_path / "tile.hkx.dcx"
    path.write_bytes(compress(_navmesh(last_edge_end=2), DCXType.BB_DS3))
    vertices, faces = read_navmesh_geometry(path)
    np.testing.assert_array_equal(vertices, [[0, 3, 0], [1, 3, 0], [1, 3, 1], [0, 3, 1], [2, 3, 1]])
    np.testing.assert_array_equal(faces, [[0, 1, 2], [0, 2, 3], [1, 4, 2]])
    assert vertices.dtype == np.float32
    assert faces.dtype == np.uint32


def test_reads_empty_tile():
    vertices, faces = read_navmesh_geometry(_navmesh(empty=True))
    assert vertices.shape == faces.shape == (0, 3)


def test_rejects_out_of_range_edges():
    with pytest.raises(ValueError, match="edge range"):
        read_navmesh_geometry(_navmesh(first_edge=-1, last_edge_end=2))


def test_rejects_open_face_loop():
    with pytest.raises(ValueError, match="edge loop"):
        read_navmesh_geometry(_navmesh())
