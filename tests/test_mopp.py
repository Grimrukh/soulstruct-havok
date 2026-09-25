"""Tests for pure-Python MOPP code reading, querying, and building (`soulstruct.havok.utilities.mopp`).

The query virtual machine is first checked against real Havok-built MOPP code (a vanilla DeS collision), which is what
justifies using it to check `build_mopp()` output.
"""
from pathlib import Path

import numpy as np
import pytest

from soulstruct.havok import HKX
from soulstruct.havok.fromsoft.shared.map_collision import MapCollisionModel
from soulstruct.havok.utilities.mopp import (
    MoppError,
    build_mopp,
    get_degenerate_triangles,
    get_mopp_terminals,
    query_mopp_aabb,
)

DES_COLLISION_PATH = Path(__file__).parent / "resources/DES/h0004b0.hkx"


def _triangle_boxes(subparts, triangle_bits=20):
    keys, mins, maxs = [], [], []
    for subpart_index, (vertices, faces) in enumerate(subparts):
        v = np.asarray(vertices, dtype=np.float32)[:, :3].astype(np.float64)
        f = np.asarray(faces)[:, :3].astype(np.int64)
        keep = ~get_degenerate_triangles(v, f)
        triangles = v[f[keep]]
        keys.extend((subpart_index << triangle_bits) | t for t in np.nonzero(keep)[0])
        mins.append(triangles.min(axis=1))
        maxs.append(triangles.max(axis=1))
    return np.array(keys), np.vstack(mins), np.vstack(maxs)


def _check_mopp(data: bytes, offset, subparts, own_box_tolerance_units=0.0, random_queries=200, seed=0):
    """Assert that MOPP code reaches exactly the non-degenerate triangles, finds each one with its own AABB, and never
    misses a brute-force AABB overlap. Returns mean hits per random query and mean true overlaps."""
    keys, mins, maxs = _triangle_boxes(subparts)
    assert get_mopp_terminals(data) == set(keys.tolist())

    eps = own_box_tolerance_units / offset[3]
    for key, lo, hi in zip(keys, mins, maxs):
        assert int(key) in query_mopp_aabb(data, offset, lo - eps, hi + eps)

    rng = np.random.default_rng(seed)
    extent = maxs.max(axis=0) - mins.min(axis=0)
    hits = true = 0
    for _ in range(random_queries):
        i = rng.integers(len(keys))
        center = (mins[i] + maxs[i]) / 2 + rng.normal(0, 0.02, 3) * extent
        half = rng.uniform(0.001, 0.02, 3) * extent
        lo, hi = center - half, center + half
        truth = set(keys[np.all((mins <= hi) & (maxs >= lo), axis=1)].tolist())
        got = query_mopp_aabb(data, offset, lo, hi)
        assert truth <= got
        hits += len(got)
        true += len(truth)
    return hits / random_queries, true / random_queries


def _des_subparts():
    model = MapCollisionModel.from_path(DES_COLLISION_PATH)
    return [(mesh.vertices, mesh.faces) for mesh in model.meshes]


def test_query_vm_on_vanilla_mopp_code():
    """Our reading of MOPP semantics must agree with real Havok-built code."""
    hkx = HKX.from_path(DES_COLLISION_PATH)
    _, physics_system = MapCollisionModel.get_hkx_physics(hkx)
    code = MapCollisionModel.get_mopp_code(physics_system)
    # Havok's own quantization differs from a float32 floor by up to ~2 root units.
    hits, true = _check_mopp(bytes(code.data), tuple(code.info.offset), _des_subparts(), own_box_tolerance_units=3)
    assert hits < 2 * true + 5  # the VM must also be selective, not just follow every branch


def test_build_mopp_vanilla_mesh():
    subparts = _des_subparts()
    data, offset = build_mopp(subparts)
    hits, true = _check_mopp(data, offset, subparts)
    assert hits < 2 * true + 5


def _grid_mesh(n=123):
    grid = np.stack(np.meshgrid(np.arange(n), np.arange(n)), -1).reshape(-1, 2).astype(np.float32)
    vertices = np.c_[grid[:, 0], np.sin(grid[:, 0] / 7) * np.cos(grid[:, 1] / 5) * 3, grid[:, 1]]
    faces = [(i * n + j, i * n + j + 1, (i + 1) * n + j) for i in range(n - 1) for j in range(n - 1)]
    faces += [(i * n + j + 1, (i + 1) * n + j + 1, (i + 1) * n + j) for i in range(n - 1) for j in range(n - 1)]
    return vertices, np.array(faces)


def test_build_mopp_large_subpart():
    """Branches over 64 KB need JUMP24 trampolines."""
    subparts = [_grid_mesh()]
    data, offset = build_mopp(subparts)
    assert len(data) > 0x10000
    _check_mopp(data, offset, subparts, random_queries=100)


def test_build_mopp_many_subparts():
    """Subparts 16+ have shape keys >= 2^24, which need 32-bit terminal offsets."""
    rng = np.random.default_rng(1)
    subparts = [
        (rng.uniform(-50, 50, (60, 3)).astype(np.float32) + i * 3, rng.integers(0, 60, (80, 3))) for i in range(20)
    ]
    data, offset = build_mopp(subparts)
    assert max(get_mopp_terminals(data)) >> 20 == 19
    _check_mopp(data, offset, subparts)


def test_build_mopp_omits_degenerate_triangles():
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [2, 0, 0], [0, 0, 1]], dtype=np.float32)
    faces = np.array([[0, 1, 2], [0, 1, 3], [0, 0, 4], [1, 2, 4]])  # 1: collinear; 2: repeated vertex
    np.testing.assert_array_equal(get_degenerate_triangles(vertices, faces), [False, True, True, False])
    data, _ = build_mopp([(vertices, faces)])
    assert get_mopp_terminals(data) == {0, 3}


def test_build_mopp_rejects_all_degenerate():
    vertices = np.zeros((3, 3), dtype=np.float32)
    with pytest.raises(MoppError):
        build_mopp([(vertices, np.array([[0, 1, 2]]))])
