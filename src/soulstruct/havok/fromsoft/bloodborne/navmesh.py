"""Read triangle geometry from Bloodborne's Havok 2014 navigation tiles."""

from __future__ import annotations

__all__ = ["read_navmesh_geometry"]

from pathlib import Path
from struct import unpack_from

import numpy as np
from soulstruct.dcx import decompress
from soulstruct.utilities.binary import BinaryReader

from soulstruct.havok.packfile.unpacker import PackFileUnpacker

# The hk2014 Face record also has user-edge and cluster fields. Triangulation needs
# only the start and count of regular directed edges.
_FACE_DTYPE = np.dtype(
    {
        "names": ["start", "count"],
        "formats": ["<i4", "<i2"],
        "offsets": [0, 8],
        "itemsize": 16,
    }
)
_EDGE_DTYPE = np.dtype(("<u4", (5,)))
_VERTEX_DTYPE = np.dtype(("<f4", (4,)))


def _read_array(data: bytes, pointers: dict[int, int], field: int, dtype: np.dtype) -> np.ndarray:
    (count,) = unpack_from("<I", data, field + 8)
    if not count:
        return np.empty(0, dtype=dtype)
    if field not in pointers:
        raise ValueError(f"Missing hkaiNavMesh array fixup at {field:#x}.")
    return np.frombuffer(data, dtype, count, pointers[field])


def _edge_ranges(starts: np.ndarray, counts: np.ndarray) -> np.ndarray:
    offsets = np.cumsum(counts) - counts
    return np.repeat(starts - offsets, counts) + np.arange(counts.sum())


def read_navmesh_geometry(source: str | Path | bytes) -> tuple[np.ndarray, np.ndarray]:
    """Return compact float32 vertices and uint32 triangles in native, tile-local coordinates.

    Accept a raw or DCX-compressed HKX member of a Bloodborne NVMHKTBND. The tile's NVA
    placement and the MSB map offset are applied by the caller.
    """
    raw = source if isinstance(source, bytes) else Path(source).read_bytes()
    if raw.startswith(b"DCX\0"):
        raw, _ = decompress(raw)

    unpacker = PackFileUnpacker()
    sections = unpacker.read_sections(BinaryReader(raw))
    header = unpacker.header
    if (
        not unpacker.hk_version.startswith("hk_2014")
        or header.pointer_size != 8
        or not header.is_little_endian
        or not header.version.has_header_extension
    ):
        raise ValueError("Expected a Bloodborne Havok 2014 navmesh packfile.")

    class_names = sections[header.classnames_section_index].raw_data
    data = sections[header.data_section_index]
    navmeshes = [
        spec.local_data_offset
        for spec in data.item_specs
        if class_names.startswith(b"hkaiNavMesh\0", spec.type_name_offset)
    ]
    if len(navmeshes) != 1:
        raise ValueError(f"Expected one hkaiNavMesh, found {len(navmeshes)}.")
    mesh = navmeshes[0]
    pointers = {pointer.source_offset: pointer.dest_offset for pointer in data.child_pointers}
    pointers.update(
        (pointer.source_offset, pointer.dest_offset)
        for pointer in data.item_pointers
        if pointer.dest_section_index == header.data_section_index
    )
    faces = _read_array(data.raw_data, pointers, mesh + 16, _FACE_DTYPE)
    edges = _read_array(data.raw_data, pointers, mesh + 32, _EDGE_DTYPE)
    vertices = _read_array(data.raw_data, pointers, mesh + 48, _VERTEX_DTYPE)[:, :3]
    if not len(faces):
        return vertices[:0], np.empty((0, 3), dtype=np.uint32)

    starts = faces["start"].astype(np.int64)
    counts = faces["count"].astype(np.int64)
    if (counts < 3).any() or (starts < 0).any() or (starts + counts > len(edges)).any():
        raise ValueError("Invalid hkaiNavMesh face edge range.")
    loop = _edge_ranges(starts, counts)
    following = loop + 1
    following[np.cumsum(counts) - 1] = starts
    if (edges[loop, 0] >= len(vertices)).any() or (edges[loop, 1] != edges[following, 0]).any():
        raise ValueError("Invalid hkaiNavMesh face edge loop.")

    rim = _edge_ranges(starts + 1, counts - 2)
    triangles = np.column_stack((edges[np.repeat(starts, counts - 2), 0], edges[rim, 0], edges[rim + 1, 0]))
    # Unreferenced steering vertices may fall far outside the walkable surface.
    used, indices = np.unique(triangles.ravel(), return_inverse=True)
    vertices = vertices[used]
    if not np.isfinite(vertices).all():
        raise ValueError("Non-finite hkaiNavMesh vertex.")
    return vertices, indices.reshape(-1, 3).astype(np.uint32)
