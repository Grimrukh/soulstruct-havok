import struct

import numpy as np
from soulstruct.dcx import DCXType, compress

from soulstruct.havok.fromsoft.bloodborne import read_collision_mesh


def _packfile(data, objects, child_pointers, item_pointers=()):
    """Construct a minimal PS4 packfile with synthetic geometry and fixups."""
    names = bytearray()
    name_offsets = {}
    for _, name in objects:
        name_offsets[name] = len(names) + 5
        names.extend(struct.pack("<IB", 0, 9) + name.encode("ascii") + b"\0")
    names.extend(b"\xff" * (-len(names) % 16))

    children = b"".join(struct.pack("<2I", source, dest) for source, dest in child_pointers)
    items = b"".join(struct.pack("<3I", source, 2, dest) for source, dest in item_pointers)
    specs = b"".join(struct.pack("<3I", offset, 0, name_offsets[name]) for offset, name in objects)

    header = bytearray(0x50)
    struct.pack_into("<4I4B4I", header, 0, 0x57E0E057, 0x10C0C010, 0, 11, 8, 1, 1, 1, 3, 2, 0, 0)
    header[0x28:0x36] = b"hk_2014.1.0-r1"
    header[0x37] = 0xFF
    struct.pack_into("<h", header, 0x3E, 16)

    def section(tag, base, offsets):
        return struct.pack("<19sB7I", tag, 0xFF, base, *offsets) + b"\xff" * 16

    names_start = len(header) + 3 * 64
    data_start = names_start + len(names)
    end = len(data) + len(children) + len(items) + len(specs)
    return bytes(
        header
        + section(b"__classnames__", names_start, [len(names)] * 6)
        + section(b"__types__", data_start, [0] * 6)
        + section(
            b"__data__",
            data_start,
            [len(data), len(data) + len(children), end - len(specs), end, end, end],
        )
        + names
        + data
        + children
        + items
        + specs
    )


def test_extract_compressed_mesh_with_local_and_shared_vertices(tmp_path):
    data = bytearray(296)
    tree = 16
    struct.pack_into("<8f", data, tree + 16, 0, 0, 0, 0, 1, 1, 1, 0)
    arrays = [(80, 160, 1), (96, 256, 2), (112, 264, 1), (128, 272, 3), (144, 288, 1)]
    for field, _, count in arrays:
        struct.pack_into("<I", data, field + 8, count)
    struct.pack_into("<6f", data, 160 + 48, 0, 0, 0, 1, 1, 1)
    struct.pack_into("<I", data, 160 + 80, 2)
    struct.pack_into("<2B", data, 160 + 88, 3, 1)
    data[256:264] = bytes([0, 1, 3, 2, 0xDE, 0xAD, 0xDE, 0xAD])
    struct.pack_into("<3I", data, 272, 0, 1, 1 << 11)
    mask = (1 << 21) - 1
    struct.pack_into("<Q", data, 288, mask | (mask << 21))

    path = tmp_path / "collision.hkx.dcx"
    raw = _packfile(data, [(0, "hknpCompressedMeshShapeData")], [(field, ptr) for field, ptr, _ in arrays])
    path.write_bytes(compress(raw, DCXType.DCX_DFLT_10000_24_9))
    vertices, faces = read_collision_mesh(path)

    np.testing.assert_array_equal(vertices, [[0, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0]])
    np.testing.assert_array_equal(faces, [[0, 1, 3], [0, 3, 2]])
    assert vertices.dtype == np.float32
    assert faces.dtype == np.uint32


def test_extract_convex_mesh_with_body_orientation_and_translation():
    data = bytearray(320)
    struct.pack_into("<HH", data, 0x28, 3, 64 - 0x28)
    struct.pack_into("<HH", data, 0x30, 1, 112 - 0x30)
    struct.pack_into("<HH", data, 0x34, 3, 116 - 0x34)
    struct.pack_into("<12f", data, 64, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0)
    struct.pack_into("<HBB", data, 112, 0, 3, 0)
    data[116:119] = bytes([0, 1, 2])

    struct.pack_into("<I", data, 200, 1)
    struct.pack_into("<3f", data, 208 + 48, 10, 20, 30)
    struct.pack_into("<4f", data, 208 + 64, 0, 0, 1, 1)
    raw = _packfile(
        data,
        [(0, "hknpConvexPolytopeShape"), (128, "hknpPhysicsSystemData")],
        child_pointers=[(192, 208)],
        item_pointers=[(208, 0)],
    )
    vertices, faces = read_collision_mesh(raw)
    np.testing.assert_allclose(vertices, [[10, 20, 30], [10, 21, 30], [9, 20, 30]])
    np.testing.assert_array_equal(faces, [[0, 1, 2]])
