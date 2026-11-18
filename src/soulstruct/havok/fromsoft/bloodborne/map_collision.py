"""Extract read-only triangle geometry from Bloodborne's PS4 map collision HKX files."""

from __future__ import annotations

__all__ = ["read_collision_mesh"]

from collections import defaultdict
from pathlib import Path
from struct import unpack_from

import numpy as np
from soulstruct.dcx import decompress
from soulstruct.utilities.binary import BinaryReader, ByteOrder

from soulstruct.havok.packfile.structs import PackFileHeader, PackFileHeaderExtension
from soulstruct.havok.packfile.unpacker import PackFileUnpacker


class _CollisionPackfile:
    """Read geometry and relocated pointers without instantiating the physics object graph."""

    def __init__(self, raw: bytes):
        if raw.startswith(b"DCX\0"):
            raw, _ = decompress(raw)
        reader = BinaryReader(raw, byte_order=ByteOrder.LittleEndian)
        header = PackFileHeader.from_bytes(reader)
        if (
            header.pointer_size != 8
            or not header.is_little_endian
            or header.reuse_padding_optimization != 1
            or not header.contents_version_string.startswith("hk_2014")
            or not header.version.has_header_extension
        ):
            raise ValueError("Expected a Bloodborne Havok 2014 PS4 packfile.")

        extension = PackFileHeaderExtension.from_bytes(reader)
        reader.seek(0x40 + extension.section_offset)
        unpacker = PackFileUnpacker(header=header, hk_version=header.contents_version_string)
        sections = [unpacker.unpack_section(reader) for _ in range(header.section_count)]
        names = sections[header.classnames_section_index]
        data = sections[header.data_section_index]
        unpacker.unpack_class_names(names.raw_data)
        self.data = data.raw_data
        self.pointers = {pointer.source_offset: pointer.dest_offset for pointer in data.child_pointers}
        self.pointers.update(
            (pointer.source_offset, pointer.dest_offset)
            for pointer in data.item_pointers
            if pointer.dest_section_index == header.data_section_index
        )
        self.objects = {
            spec.local_data_offset: unpacker.class_names[spec.type_name_offset] for spec in data.item_specs
        }

    def array(self, offset: int, dtype: str, width: int = 1) -> np.ndarray:
        (count,) = unpack_from("<I", self.data, offset + 8)
        if count == 0:
            return np.empty((0, width), dtype=dtype) if width > 1 else np.empty(0, dtype=dtype)
        pointer = self.pointers.get(offset)
        if pointer is None:
            raise ValueError(f"Missing geometry array fixup at {offset:#x}.")
        values = np.frombuffer(self.data, dtype, count * width, pointer)
        return values.reshape(count, width) if width > 1 else values

    def relative_array(self, offset: int, dtype: str, width: int = 1) -> np.ndarray:
        """Read a PS4 hkRelArray, whose data offset is relative to the array field."""
        count, delta = unpack_from("<HH", self.data, offset)
        return np.frombuffer(self.data, dtype, count * width, offset + delta).reshape(count, width)


def _combine(meshes) -> tuple[np.ndarray, np.ndarray]:
    vertices, faces = [], []
    vertex_count = 0
    for xyz, indices in meshes:
        vertices.append(xyz)
        faces.append(indices + vertex_count)
        vertex_count += len(xyz)
    if not vertices:
        return np.empty((0, 3), dtype=np.float32), np.empty((0, 3), dtype=np.uint32)
    return np.concatenate(vertices).astype(np.float32), np.concatenate(faces).astype(np.uint32)


def _compressed_sections(hkx: _CollisionPackfile, tree: int):
    domain = np.frombuffer(hkx.data, "<f4", 8, tree + 16).reshape(2, 4)[:, :3]
    primitives = hkx.array(tree + 80, "u1", 4)
    shared_indices = hkx.array(tree + 96, "<u2")
    packed = hkx.array(tree + 112, "<u4")
    shared = hkx.array(tree + 128, "<u8")
    # Shared vertices use 21/21/22 bits and are quantized against the tree's AABB.
    mask = (1 << 21) - 1
    components = np.column_stack((shared & mask, (shared >> 21) & mask, shared >> 42))
    shared_xyz = domain[0] + components * ((domain[1] - domain[0]) / [mask, mask, (1 << 22) - 1])
    for section in hkx.array(tree + 64, "u1", 96):
        origin, scale = np.frombuffer(section, "<f4", 6, 48).reshape(2, 3)
        first, shared_window, primitive_window = unpack_from("<III", section, 72)
        local_count, shared_count = section[88:90].tolist()
        # Section-local vertices use 11/11/10 bits and the section's offset and scale.
        v = packed[first : first + local_count]
        local_xyz = np.column_stack((v & 2047, (v >> 11) & 2047, v >> 22)) * scale + origin
        shared_start = shared_window >> 8
        xyz = np.concatenate((local_xyz, shared_xyz[shared_indices[shared_start : shared_start + shared_count]]))
        start, count = primitive_window >> 8, primitive_window & 255
        quads = primitives[start : start + count]
        quads = quads[~np.all(quads == [0xDE, 0xAD, 0xDE, 0xAD], axis=1)]
        if not len(quads):
            continue
        if quads.max() >= len(xyz):
            raise ValueError("Compressed mesh primitive references an absent vertex.")
        extra = quads[quads[:, 2] != quads[:, 3]]
        yield xyz, np.concatenate((quads[:, :3], extra[:, [0, 2, 3]])).astype(np.uint32)


def _convex_mesh(hkx: _CollisionPackfile, shape: int) -> tuple[np.ndarray, np.ndarray]:
    xyz = hkx.relative_array(shape + 0x28, "<f4", 4)[:, :3]
    indices = hkx.relative_array(shape + 0x34, "u1").ravel()
    triangles = []
    for face in hkx.relative_array(shape + 0x30, "u1", 4):
        first, count = unpack_from("<HB", face)
        polygon = indices[first : first + count]
        if len(polygon) != count or (count and polygon.max() >= len(xyz)):
            raise ValueError("Convex polytope face references an absent vertex.")
        triangles.extend((polygon[0], polygon[i], polygon[i + 1]) for i in range(1, count - 1))
    return xyz, np.asarray(triangles, dtype=np.uint32).reshape(-1, 3)


def _body_placements(hkx: _CollisionPackfile, geometry: dict):
    placements = defaultdict(list)
    has_bodies = False
    has_shapes = False
    for offset, class_name in hkx.objects.items():
        if class_name != "hknpPhysicsSystemData":
            continue
        field = offset + 64
        (count,) = unpack_from("<I", hkx.data, field + 8)
        if not count:
            continue
        has_bodies = True
        start = hkx.pointers[field]
        for index in range(count):
            body = start + 96 * index
            shape = hkx.pointers.get(body)
            if shape is None:
                continue
            has_shapes = True
            # A compressed shape wrapper points to the geometry in one of these two layouts.
            model = next(
                (
                    model
                    for model in (shape, hkx.pointers.get(shape + 88), hkx.pointers.get(shape + 96))
                    if model in geometry
                ),
                None,
            )
            if model is None:
                continue
            position = np.frombuffer(hkx.data, "<f4", 3, body + 48)
            orientation = np.frombuffer(hkx.data, "<f4", 4, body + 64)
            length = np.linalg.norm(orientation)
            if not np.isfinite(length) or length < 1e-8:
                raise ValueError("Invalid collision body orientation.")
            placements[model].append((position, orientation / length))
    return placements, has_bodies and not has_shapes


def read_collision_mesh(source: str | Path | bytes) -> tuple[np.ndarray, np.ndarray]:
    """Return native Y-up float32 vertices and uint32 triangles, with HKX body poses applied.

    Accepts a raw or DCX-compressed HKX from a Bloodborne map collision binder. Supports compressed
    mesh data and convex polytopes. Apply the MSB part placement separately to obtain map coordinates.
    """
    hkx = _CollisionPackfile(source if isinstance(source, bytes) else Path(source).read_bytes())
    geometry = {}
    for offset, class_name in hkx.objects.items():
        if class_name == "hknpCompressedMeshShapeData":
            geometry[offset] = _combine(_compressed_sections(hkx, offset + 16))
        elif class_name == "hknpConvexPolytopeShape":
            geometry[offset] = _convex_mesh(hkx, offset)

    placements, empty_bodies = _body_placements(hkx, geometry)
    if not geometry and not empty_bodies:
        raise ValueError("No supported Bloodborne collision shape.")

    meshes = []
    for model, (xyz, faces) in geometry.items():
        poses = placements.get(model)
        if not poses:
            meshes.append((xyz, faces))
            continue
        for position, orientation in poses:
            # Apply q * v * conjugate(q) without creating a quaternion for each vertex.
            edge = 2 * np.cross(orientation[:3], xyz)
            rotated = xyz + orientation[3] * edge + np.cross(orientation[:3], edge)
            meshes.append((rotated + position, faces))
    return _combine(meshes)
