"""Pure-Python reading, querying, and building of Havok MOPP code (`hkpMoppCode`) for FromSoft map collisions.

MOPP ("Memory Optimized Partial Polytope") code is a compact bytecode encoding of a bounding volume tree over the
triangles of an `hkpExtendedMeshShape`, used by `hkpMoppBvTreeShape` in Demon's Souls and Dark Souls 1 (PTDE/DSR).

Query space: world positions are mapped to unsigned 24-bit integers per axis with `hkpMoppCode.info.offset`, where
`(x, y, z)` is the world-space origin and `w` is the scale: `int = floor((world - offset.xyz) * offset.w)` (float32).
Commands compare only the high byte (`int >> 16`) of each query coordinate in the current 'frame'; the rescale commands
zoom the frame into a sub-region to regain precision further down the tree.

Commands (all multi-byte arguments are big-endian on every platform). Semantics were reverse-engineered from vanilla
DeS/DSR files and `mopper` (Havok 2012) output, and validated by checking that `query_mopp_aabb()` finds every triangle
(and every brute-force AABB overlap) in hundreds of real MOPP codes. Commands marked * were never seen in real code.

    0x00            RETURN
    0x01-0x04       RESCALE by 1-4 bits: [x, y, z] frame offsets; `q = (q - (arg << 16)) << bits`
    0x05-0x07       JUMP 8/16/24 bits: `pc = next_pc + jump` (0x08* presumably 32 bits)
    0x09-0x0A       TERMINAL OFFSET += 8/16-bit value
    0x0B            TERMINAL OFFSET = 32-bit value (only ever seen with a prior offset of zero)
    0x0C            JUMP CHUNK: `pc = arg16 * 512` (DeS code built with chunk subdivision; chunks padded with 0xCD)
    0x10-0x1C       SPLIT on a plane (x, y, z, then diagonals): [left_max, right_min, right_jump8]
    0x20-0x22       SINGLE SPLIT on x/y/z: [value, right_jump8]
    0x23-0x25       SPLIT on x/y/z with 16-bit jumps: [left_max, right_min, left_jump16, right_jump16]
    0x26-0x28       BOUNDS on x/y/z: [min, max] (exit if query is outside)
    0x29-0x2B       BOUNDS on x/y/z with full 24-bit precision: [min24, max24], in ROOT space (ignores rescaling)
    0x30-0x4F       TERMINAL (offset + 0..31)
    0x50-0x52       TERMINAL (offset + 8/16/24-bit value) (0x53* presumably 32 bits)
    0x70            JUMP ABSOLUTE: `pc = arg32` (DS1 code built with chunk subdivision; blocks padded with 0xCD)

A split's left branch is followed if the query's minimum is <= `left_max`, and its right branch if the query's maximum
is >= `right_min` (both, if the query straddles the plane).

A 'terminal' is a shape key, which for FromSoft extended mesh shapes is `(subpart_index << 20) | triangle_index`
(see `hkpExtendedMeshShape.numBitsForSubpartIndex`, which is always 12).

`build_mopp()` only emits commands that appear in real `mopper` output: axis-aligned splits, rescales, root bounds,
JUMP24 trampolines for large branches, terminal offsets, and terminals. It does not use chunk subdivision, which
the old `mopper` executable doesn't either.
"""
from __future__ import annotations

__all__ = [
    "MoppError",
    "MOPP_CHUNK_SIZE",
    "DEGENERATE_CROSS_SQUARED",
    "get_mopp_terminals",
    "quantize_aabb",
    "query_mopp_aabb",
    "get_degenerate_triangles",
    "build_mopp",
]

import typing as tp

import numpy as np

# Axis (0, 1, 2) of each single-axis command family.
_AXIS_SPLIT_8 = {0x10: 0, 0x11: 1, 0x12: 2}
_AXIS_SINGLE_SPLIT = {0x20: 0, 0x21: 1, 0x22: 2}
_AXIS_SPLIT_16 = {0x23: 0, 0x24: 1, 0x25: 2}
_AXIS_BOUNDS = {0x26: 0, 0x27: 1, 0x28: 2}


# Chunk size of MOPP code built with chunk subdivision (for PS3 SPUs); `JUMP_CHUNK` targets a chunk index.
MOPP_CHUNK_SIZE = 512


class MoppError(Exception):
    pass


def _be(data: bytes, i: int, n: int) -> int:
    return int.from_bytes(data[i:i + n], "big")


def get_mopp_terminals(data: bytes) -> set[int]:
    """Walk every branch of MOPP `data` and return the set of all reachable terminal shape keys."""
    terminals = set()
    stack = [(0, 0)]  # (pc, terminal offset)
    visited = set()
    while stack:
        pc, offset = stack.pop()
        while (pc, offset) not in visited:
            visited.add((pc, offset))
            op = data[pc]
            if op == 0x00:
                break
            elif 0x01 <= op <= 0x04:
                pc += 4
            elif 0x05 <= op <= 0x08:
                size = op - 0x04
                pc += 1 + size + _be(data, pc + 1, size)
            elif op == 0x0C:
                pc = _be(data, pc + 1, 2) * MOPP_CHUNK_SIZE
            elif op == 0x09:
                offset += data[pc + 1]
                pc += 2
            elif op == 0x0A:
                offset += _be(data, pc + 1, 2)
                pc += 3
            elif op == 0x0B:
                offset = _be(data, pc + 1, 4)
                pc += 5
            elif 0x10 <= op <= 0x1C:
                stack.append((pc + 4 + data[pc + 3], offset))
                pc += 4
            elif 0x20 <= op <= 0x22:
                stack.append((pc + 3 + data[pc + 2], offset))
                pc += 3
            elif 0x23 <= op <= 0x25:
                stack.append((pc + 7 + _be(data, pc + 5, 2), offset))
                pc += 7 + _be(data, pc + 3, 2)
            elif 0x26 <= op <= 0x28:
                pc += 3
            elif 0x29 <= op <= 0x2B:
                pc += 7
            elif op == 0x70:
                pc = _be(data, pc + 1, 4)
            elif 0x30 <= op <= 0x4F:
                terminals.add(offset + op - 0x30)
                break
            elif 0x50 <= op <= 0x53:
                terminals.add(offset + _be(data, pc + 1, op - 0x4F))
                break
            else:
                raise MoppError(f"Unknown MOPP command 0x{op:02X} at {pc}.")
    return terminals


def quantize_aabb(
    aabb_min: tp.Sequence[float], aabb_max: tp.Sequence[float], code_offset: tp.Sequence[float]
) -> tuple[list[int], list[int]]:
    """Convert a world-space AABB to MOPP root integer space using `hkpMoppCode.info.offset` (x, y, z, scale).

    Uses `float32` arithmetic like Havok, which matters for coordinates that land exactly on a byte boundary.
    """
    offset = np.asarray(code_offset, dtype=np.float32)
    q_min = np.floor((np.asarray(aabb_min, dtype=np.float32) - offset[:3]) * offset[3])
    q_max = np.floor((np.asarray(aabb_max, dtype=np.float32) - offset[:3]) * offset[3])
    return [int(v) for v in q_min], [int(v) for v in q_max]


def query_mopp_aabb(
    data: bytes,
    code_offset: tp.Sequence[float],
    aabb_min: tp.Sequence[float],
    aabb_max: tp.Sequence[float],
) -> set[int]:
    """Run an AABB query through MOPP `data` and return the terminal shape keys that it can't rule out.

    Diagonal split planes (0x13-0x1C) are not modelled precisely: both of their branches are always followed, which is
    conservative (never loses a terminal) but less selective than the real virtual machine.
    """
    q_min, q_max = quantize_aabb(aabb_min, aabb_max, code_offset)
    terminals = set()
    stack = [(0, 0, tuple(q_min), tuple(q_max))]
    while stack:
        pc, offset, lo, hi = stack.pop()
        while True:
            op = data[pc]
            if op == 0x00:
                break
            elif 0x01 <= op <= 0x04:
                shift = op
                lo = tuple((lo[i] - (data[pc + 1 + i] << 16)) << shift for i in range(3))
                hi = tuple((hi[i] - (data[pc + 1 + i] << 16)) << shift for i in range(3))
                pc += 4
            elif 0x05 <= op <= 0x08:
                size = op - 0x04
                pc += 1 + size + _be(data, pc + 1, size)
            elif op == 0x0C:
                pc = _be(data, pc + 1, 2) * MOPP_CHUNK_SIZE
            elif op == 0x09:
                offset += data[pc + 1]
                pc += 2
            elif op == 0x0A:
                offset += _be(data, pc + 1, 2)
                pc += 3
            elif op == 0x0B:
                offset = _be(data, pc + 1, 4)
                pc += 5
            elif 0x10 <= op <= 0x1C:
                left_pc, right_pc = pc + 4, pc + 4 + data[pc + 3]
                if op in _AXIS_SPLIT_8:
                    axis = _AXIS_SPLIT_8[op]
                    go_left = (lo[axis] >> 16) <= data[pc + 1]
                    go_right = (hi[axis] >> 16) >= data[pc + 2]
                else:
                    go_left = go_right = True  # diagonal plane: conservative
                if go_right:
                    stack.append((right_pc, offset, lo, hi))
                if not go_left:
                    break
                pc = left_pc
            elif 0x20 <= op <= 0x22:
                axis = _AXIS_SINGLE_SPLIT[op]
                left_pc, right_pc = pc + 3, pc + 3 + data[pc + 2]
                go_left = (lo[axis] >> 16) <= data[pc + 1]
                go_right = (hi[axis] >> 16) >= data[pc + 1]
                if go_right:
                    stack.append((right_pc, offset, lo, hi))
                if not go_left:
                    break
                pc = left_pc
            elif 0x23 <= op <= 0x25:
                axis = _AXIS_SPLIT_16[op]
                left_pc, right_pc = pc + 7 + _be(data, pc + 3, 2), pc + 7 + _be(data, pc + 5, 2)
                go_left = (lo[axis] >> 16) <= data[pc + 1]
                go_right = (hi[axis] >> 16) >= data[pc + 2]
                if go_right:
                    stack.append((right_pc, offset, lo, hi))
                if not go_left:
                    break
                pc = left_pc
            elif 0x26 <= op <= 0x28:
                axis = _AXIS_BOUNDS[op]
                if (hi[axis] >> 16) < data[pc + 1] or (lo[axis] >> 16) > data[pc + 2]:
                    break
                pc += 3
            elif 0x29 <= op <= 0x2B:
                axis = op - 0x29
                # Compared against the root query, unaffected by rescaling.
                if q_max[axis] < _be(data, pc + 1, 3) or q_min[axis] > _be(data, pc + 4, 3):
                    break
                pc += 7
            elif op == 0x70:
                pc = _be(data, pc + 1, 4)
            elif 0x30 <= op <= 0x4F:
                terminals.add(offset + op - 0x30)
                break
            elif 0x50 <= op <= 0x53:
                terminals.add(offset + _be(data, pc + 1, op - 0x4F))
                break
            else:
                raise MoppError(f"Unknown MOPP command 0x{op:02X} at {pc}.")
    return terminals


# Havok (and `mopper`) omit triangles whose (float32) edge cross product has a squared length below this, taken from
# either of their first two vertices. This reproduces 1584 of the 1588 triangles `mopper` drops from vanilla DeS maps,
# with no false positives (the other four are merely kept, which is harmless).
DEGENERATE_CROSS_SQUARED = 1e-7

# Root-space units by which each quantized triangle AABB is expanded, so builds never depend on exact float rounding
# (Havok's own quantization differs from a plain float32 floor by up to ~2 units). One unit is ~6e-8 of the extent.
_TRIANGLE_PADDING = 4

# A node's frame is only rescaled if it can zoom in by at least this many bits (each rescale costs four bytes).
_MIN_RESCALE_BITS = 2

_ROOT_MAX = (1 << 24) - 1


def get_degenerate_triangles(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    """Return a boolean mask of `faces` that Havok's MOPP builder would omit as degenerate."""
    v = np.asarray(vertices, dtype=np.float32)[:, :3]
    f = np.asarray(faces)[:, :3].astype(np.int64)
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    tolerance = np.float32(DEGENERATE_CROSS_SQUARED)
    cross_a = np.sum(np.cross(a - b, a - c) ** 2, axis=1)
    cross_b = np.sum(np.cross(b - a, b - c) ** 2, axis=1)
    return (cross_a < tolerance) | (cross_b < tolerance)


def build_mopp(
    subparts: tp.Sequence[tuple[np.ndarray, np.ndarray]],
    num_bits_for_subpart_index: int = 12,
) -> tuple[bytes, tuple[float, float, float, float]]:
    """Build MOPP code over the triangles of `hkpExtendedMeshShape` subparts, given as `(vertices, faces)` arrays.

    Returns `(data, info_offset)` for `hkpMoppCode.data` and `hkpMoppCode.info.offset` (x, y, z, scale). Terminals are
    shape keys `(subpart_index << (32 - num_bits_for_subpart_index)) | triangle_index`. Degenerate triangles are
    omitted, as Havok does (see `get_degenerate_triangles()`).
    """
    triangle_bits = 32 - num_bits_for_subpart_index
    if len(subparts) > 1 << num_bits_for_subpart_index:
        raise MoppError(f"Too many subparts ({len(subparts)}) for {num_bits_for_subpart_index} subpart index bits.")

    keys_list, mins_list, maxs_list = [], [], []
    for subpart_index, (vertices, faces) in enumerate(subparts):
        faces = np.asarray(faces)[:, :3].astype(np.int64)
        if len(faces) > 1 << triangle_bits:
            raise MoppError(f"Subpart {subpart_index} has too many triangles ({len(faces)}) for its shape keys.")
        v = np.asarray(vertices, dtype=np.float32)[:, :3].astype(np.float64)
        keep = ~get_degenerate_triangles(vertices, faces)
        triangles = v[faces[keep]]  # (n, 3, 3)
        keys_list.append((subpart_index << triangle_bits) | np.nonzero(keep)[0])
        mins_list.append(triangles.min(axis=1))
        maxs_list.append(triangles.max(axis=1))
    keys = np.concatenate(keys_list).astype(np.int64)
    if len(keys) == 0:
        raise MoppError("Cannot build MOPP code: no non-degenerate triangles.")
    triangle_mins = np.vstack(mins_list)
    triangle_maxs = np.vstack(maxs_list)

    # Same quantization as Havok: the largest axis extent maps to 254 (of 256) high-byte units.
    world_min = triangle_mins.min(axis=0)
    world_max = triangle_maxs.max(axis=0)
    extent = max(float((world_max - world_min).max()), 1e-6)
    margin = extent * 1e-5
    origin = (world_min - margin).astype(np.float32)
    scale = np.float32(254 * 65536 / (extent + 2 * margin))
    origin64, scale64 = origin.astype(np.float64), float(scale)  # use exactly the stored (float32) values
    lo = np.floor((triangle_mins - origin64) * scale64).astype(np.int64) - _TRIANGLE_PADDING
    hi = np.floor((triangle_maxs - origin64) * scale64).astype(np.int64) + _TRIANGLE_PADDING
    lo = np.clip(lo, 0, _ROOT_MAX)
    hi = np.clip(hi, 0, _ROOT_MAX)

    builder = _MoppBuilder(keys, lo, hi, triangle_bits)
    code = builder.build(np.arange(len(keys)), np.zeros(3, dtype=np.int64), 0, 0, _UNBOUNDED)
    info_offset = (float(origin[0]), float(origin[1]), float(origin[2]), float(scale))
    return code, info_offset


# Per-axis `(min, max)` high-byte intervals that queries reaching a node are already known to overlap.
_UNBOUNDED = ((-1 << 40, 1 << 40),) * 3


class _MoppBuilder:
    """Recursive median-split bounding volume tree builder that emits MOPP commands.

    Triangle bounds are held in root space (unsigned 24-bit ints). Each node's frame is `(origin, shift)`, under which a
    root value `c` has frame value `(c - origin) << shift` and a high byte of `frame_value >> 16` (always 0-255 for the
    node's own triangles).
    """

    def __init__(self, keys: np.ndarray, lo: np.ndarray, hi: np.ndarray, triangle_bits: int):
        self.keys = keys
        self.lo = lo
        self.hi = hi
        self.centroids = lo + hi  # (doubled) triangle AABB centers, for ordering only
        self.triangle_bits = triangle_bits

    def build(
        self,
        indices: np.ndarray,
        origin: np.ndarray,
        shift: int,
        terminal_offset: int,
        known: tuple[tuple[int, int], ...],
    ) -> bytes:
        """Emit code for the triangles at `indices`.

        `known` holds, per axis, the high-byte interval (in the current frame) that every query reaching this node is
        already known to overlap, from earlier splits and bounds; a new bounds command is emitted where this node's own
        triangles are tighter.
        """
        code = bytearray()
        keys = self.keys[indices]
        key_min, key_max = int(keys.min()), int(keys.max())

        # Terminal offsets, so that terminals below can use fewer bytes.
        subpart = key_min >> self.triangle_bits
        if terminal_offset == 0 and subpart > 0 and (key_max >> self.triangle_bits) == subpart:
            # Set once per subtree of a single non-zero subpart. (Only emitted with a zero prior offset, which is also
            # the only way Havok's builder has been seen to use it, so 'set' vs. 'add' semantics can't matter.)
            terminal_offset = subpart << self.triangle_bits
            code += b"\x0B" + terminal_offset.to_bytes(4, "big")
        delta = key_min - terminal_offset
        if key_max - terminal_offset > 0xFF and key_max - key_min <= 0xFF and 0 < delta <= 0xFFFF:
            code += bytes((0x09, delta)) if delta <= 0xFF else b"\x0A" + delta.to_bytes(2, "big")
            terminal_offset += delta

        lo_frame = (self.lo[indices] - origin) << shift
        hi_frame = (self.hi[indices] - origin) << shift

        # Rescale (zoom) the frame to this node's bounds, if that gains enough precision.
        if shift < 16 and len(indices) > 1:
            byte_min = lo_frame.min(axis=0) >> 16  # new frame origin, in current high-byte units
            span = int((hi_frame.max(axis=0) - (byte_min << 16)).max())
            bits = 0
            while bits < 4 and shift + bits < 16 and (span << (bits + 1)) <= _ROOT_MAX:
                bits += 1
            if bits >= _MIN_RESCALE_BITS:
                code += bytes((bits, *(int(b) for b in byte_min)))
                origin = origin + (byte_min << (16 - shift))
                shift += bits
                lo_frame = (self.lo[indices] - origin) << shift
                hi_frame = (self.hi[indices] - origin) << shift
                # A query high byte >= `min` (or <= `max`) in the old frame maps to these bounds in the new one.
                known = tuple(
                    ((k_min - int(a)) << bits, ((k_max + 1 - int(a)) << bits) - 1)
                    for (k_min, k_max), a in zip(known, byte_min)
                )

        # Bound any axis on which this node's triangles are tighter than what queries are already known to overlap.
        node_min = lo_frame.min(axis=0) >> 16
        node_max = hi_frame.max(axis=0) >> 16
        new_known = []
        for axis in range(3):
            b_min, b_max = int(node_min[axis]), int(node_max[axis])
            k_min, k_max = known[axis]
            if b_min > k_min or b_max < k_max:
                code += bytes((0x26 + axis, b_min, b_max))
                new_known.append((b_min, b_max))
            else:
                new_known.append((k_min, k_max))
        known = tuple(new_known)

        if len(indices) == 1:
            code += self._terminal(key_min - terminal_offset)
            return bytes(code)

        # Median split along the axis of greatest centroid spread.
        centroids = self.centroids[indices]
        axis = int(np.argmax(centroids.max(axis=0) - centroids.min(axis=0)))
        half = len(indices) // 2
        order = np.argpartition(centroids[:, axis], half)
        left_order, right_order = order[:half], order[half:]
        left_max = int(hi_frame[left_order, axis].max()) >> 16
        right_min = int(lo_frame[right_order, axis].min()) >> 16
        # Split tests also tell each branch one side of the interval that its queries must overlap.
        left_known = list(known)
        left_known[axis] = (known[axis][0], min(known[axis][1], left_max))
        right_known = list(known)
        right_known[axis] = (max(known[axis][0], right_min), known[axis][1])
        left_code = self.build(indices[left_order], origin, shift, terminal_offset, tuple(left_known))
        right_code = self.build(indices[right_order], origin, shift, terminal_offset, tuple(right_known))

        n = len(left_code)
        if n <= 0xFF:
            code += bytes((0x10 + axis, left_max, right_min, n))
        elif n <= 0xFFFF:
            code += bytes((0x23 + axis, left_max, right_min)) + b"\x00\x00" + n.to_bytes(2, "big")
        else:
            # Left branch skips a JUMP24 trampoline, which the right branch uses to skip the left branch.
            code += bytes((0x23 + axis, left_max, right_min)) + b"\x00\x04\x00\x00"
            code += b"\x07" + n.to_bytes(3, "big")
        code += left_code
        code += right_code
        return bytes(code)

    @staticmethod
    def _terminal(value: int) -> bytes:
        if value < 0x20:
            return bytes((0x30 + value,))
        if value <= 0xFF:
            return bytes((0x50, value))
        if value <= 0xFFFF:
            return b"\x51" + value.to_bytes(2, "big")
        if value <= 0xFFFFFF:
            return b"\x52" + value.to_bytes(3, "big")
        raise MoppError(f"MOPP terminal value too large: {value:#x}")
