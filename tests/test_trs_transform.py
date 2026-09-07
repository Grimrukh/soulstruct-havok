"""Unit tests for `soulstruct.havok.utilities.maths.trs_transform.TRSTransform`."""
from __future__ import annotations

import numpy as np
import pytest

from soulstruct.utilities.maths import Vector3
from soulstruct.havok.utilities.maths.quaternion import Quaternion
from soulstruct.havok.utilities.maths.trs_transform import TRSTransform


def _rotation(axis=(0.3, 0.5, 0.81), degrees=63.0) -> Quaternion:
    return Quaternion.from_axis_angle(Vector3(axis), degrees)


# region Inverse

def test_inverse_of_identity_is_identity():
    assert TRSTransform.identity().inverse().is_identity()


def test_left_inverse_is_exact_for_unit_scale():
    t = TRSTransform(Vector3((1.5, -2.0, 0.75)), _rotation(), Vector3.one())
    assert (t.inverse() @ t).is_identity()


def test_left_inverse_is_exact_for_uniform_scale():
    """Regression test: scale must be applied to the translation before it is rotated.

    The previous implementation ignored scale entirely when inverting the translation, leaving a
    residual translation of `R^-1 * (T - T / S)`. That silently corrupted every armature-space to
    local-space conversion for any animation with animated scale.
    """
    t = TRSTransform(Vector3((1.5, -2.0, 0.75)), _rotation(), Vector3((1.0268, 1.0268, 1.0268)))
    assert (t.inverse() @ t).is_identity()


def test_left_inverse_is_exact_for_non_uniform_scale():
    t = TRSTransform(Vector3((1.5, -2.0, 0.75)), _rotation(), Vector3((0.7, 1.3, 2.2)))
    assert (t.inverse() @ t).is_identity()


def test_inverse_undoes_composition_with_scale():
    """`parent.inverse() @ (parent @ local)` must recover `local` (armature space -> local space)."""
    parent = TRSTransform(Vector3((-0.026, 0.0, 0.313)), _rotation(), Vector3((1.0268, 1.0268, 1.0268)))
    local = TRSTransform(Vector3((-0.3131, 0.1935, 0.0208)), _rotation((1.0, 0.0, 0.0), 12.0), Vector3((0.9739,) * 3))

    recovered = parent.inverse() @ (parent @ local)

    assert np.allclose(recovered.translation.data, local.translation.data)
    assert recovered.rotation.is_same_rotation(local.rotation)
    assert np.allclose(recovered.scale.data, local.scale.data)


def test_inverse_rotation_and_scale_components():
    t = TRSTransform(Vector3((1.0, 2.0, 3.0)), _rotation(), Vector3((2.0, 4.0, 0.5)))
    inv = t.inverse()
    assert inv.rotation.is_same_rotation(t.rotation.inverse())
    assert np.allclose(inv.scale.data, [0.5, 0.25, 2.0])


def test_inverse_translation_unchanged_for_unit_scale():
    """Guard: the fix must not alter behaviour for the (very common) unit-scale case."""
    t = TRSTransform(Vector3((1.0, 2.0, 3.0)), _rotation(), Vector3.one())
    expected = -t.rotation.inverse().rotate_vector(t.translation)
    assert np.allclose(t.inverse().translation.data, expected.data)


def test_inverse_is_involutive_for_uniform_scale():
    t = TRSTransform(Vector3((1.5, -2.0, 0.75)), _rotation(), Vector3((1.0268,) * 3))
    round_tripped = t.inverse().inverse()
    assert np.allclose(round_tripped.translation.data, t.translation.data)
    assert round_tripped.rotation.is_same_rotation(t.rotation)
    assert np.allclose(round_tripped.scale.data, t.scale.data)

# endregion


# region Vector transformation

def test_inverse_transform_vector_undoes_transform_vector_with_scale():
    """Regression test: this is broken by an inverse that ignores scale."""
    t = TRSTransform(Vector3((-0.026, 0.0, 0.313)), _rotation(), Vector3((1.0268,) * 3))
    v = Vector3((0.3, -1.2, 4.5))
    assert np.allclose(t.inverse_transform_vector(t.transform_vector(v)).data, v.data)


def test_inverse_transform_vector_undoes_transform_vector_with_unit_scale():
    t = TRSTransform(Vector3((-0.026, 0.0, 0.313)), _rotation(), Vector3.one())
    v = Vector3((0.3, -1.2, 4.5))
    assert np.allclose(t.inverse_transform_vector(t.transform_vector(v)).data, v.data)

# endregion


# region Hierarchy round-trip

@pytest.mark.parametrize("scales", [
    [1.0, 1.0, 1.0, 1.0],
    [1.0268, 0.9739, 1.0099, 0.9812],  # observed c1200 (Large Rat) animated scales
])
def test_armature_to_local_round_trip_down_a_bone_chain(scales):
    """Accumulated error down a hierarchy must stay negligible.

    This mirrors what `AnimationContainer.local_transforms_to_armature_transforms()` and its inverse
    do for every animation frame, which is where the original bug surfaced.
    """
    locals_ = [
        TRSTransform(Vector3((0.1 * i, -0.2 * i, 0.3)), _rotation(degrees=11.0 * i), Vector3((s, s, s)))
        for i, s in enumerate(scales)
    ]

    # Local -> armature space (forward kinematics).
    arma = []
    parent = TRSTransform.identity()
    for local in locals_:
        parent = parent @ local
        arma.append(parent)

    # Armature -> local space (what the exporter does).
    recovered = [arma[0]]
    for i in range(1, len(arma)):
        recovered.append(arma[i - 1].inverse() @ arma[i])

    for original, result in zip(locals_, recovered):
        assert np.allclose(original.translation.data, result.translation.data, atol=1e-9)
        assert np.allclose(original.scale.data, result.scale.data, atol=1e-9)
        assert original.rotation.is_same_rotation(result.rotation)

# endregion
