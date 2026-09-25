"""Demon's Souls (Havok 5.5.0) map collision round-trip tests.

These guard against exports that load fine in Soulstruct/DSMapStudio but only half-work in-game. In particular, the
game decodes each MOPP shape key into `(subpart index, triangle index)` using the shape's `numBitsForSubpartIndex`, so
if that isn't written, every subpart after the first (i.e. every material after the first) has no collision.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

from soulstruct.havok import HKX
from soulstruct.havok.fromsoft.shared.map_collision import MapCollisionModel
from soulstruct.havok.utilities.mopp import get_degenerate_triangles, get_mopp_terminals

DES_COLLISION_PATH = Path(__file__).parent / "resources/DES/h0004b0.hkx"


def _check_physics(hkx: HKX, model: MapCollisionModel):
    _, physics_system = MapCollisionModel.get_hkx_physics(hkx)
    child_shape, shape_type = MapCollisionModel.get_child_shape(physics_system)
    assert shape_type == "CUSTOM"
    rigid_body = physics_system.rigidBodies[0]

    assert child_shape.numBitsForSubpartIndex == 12
    assert physics_system.active is True
    assert rigid_body.collidable.broadPhaseHandle.objectQualityType == 1  # keyframed

    center = np.array(child_shape.aabbCenter)[:3]
    half_extents = np.array(child_shape.aabbHalfExtents)[:3]
    assert rigid_body.motion.motionState.objectRadius == pytest.approx(
        np.linalg.norm(center) + np.linalg.norm(half_extents), rel=1e-5
    )

    # Every (non-degenerate) triangle of every subpart must be reachable through the MOPP code, using the game's shape
    # key encoding.
    terminals = get_mopp_terminals(bytes(MapCollisionModel.get_mopp_code(physics_system).data))
    triangle_bits = 32 - child_shape.numBitsForSubpartIndex
    decoded = {(key >> triangle_bits, key & ((1 << triangle_bits) - 1)) for key in terminals}
    expected = {
        (i, int(t))
        for i, mesh in enumerate(model.meshes)
        for t in np.nonzero(~get_degenerate_triangles(mesh.vertices, mesh.faces))[0]
    }
    assert decoded == expected


def test_des_vanilla_collision_fields():
    hkx = HKX.from_path(DES_COLLISION_PATH)
    model = MapCollisionModel.from_hkx(hkx)
    assert len(model.meshes) > 1, "Test resource must have multiple subparts to be meaningful."
    _check_physics(hkx, model)


@pytest.mark.parametrize("mopp_builder", [
    "python",
    pytest.param("mopper", marks=pytest.mark.skipif(sys.platform != "win32", reason="mopper.exe is Windows-only")),
])
def test_des_collision_export_round_trip(tmp_path, mopp_builder):
    model = MapCollisionModel.from_path(DES_COLLISION_PATH)
    export_path = tmp_path / "h0004b0.hkx"
    export_path.write_bytes(bytes(model.to_hkx(mopp_builder=mopp_builder).to_writer()))

    re_hkx = HKX.from_path(export_path)
    re_model = MapCollisionModel.from_hkx(re_hkx)
    assert [m.material_index for m in re_model.meshes] == [m.material_index for m in model.meshes]
    for mesh, re_mesh in zip(model.meshes, re_model.meshes, strict=True):
        np.testing.assert_array_equal(mesh.vertices, re_mesh.vertices)
        np.testing.assert_array_equal(mesh.faces, re_mesh.faces)
    _check_physics(re_hkx, re_model)
