"""Unit tests for `soulstruct.havok.utilities.maths.quaternion.Quaternion`."""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy.spatial.transform import Rotation

from soulstruct.utilities.maths import Vector3, Matrix3
from soulstruct.havok.utilities.maths.quaternion import Quaternion


# region Construction

def test_construct_from_list():
    q = Quaternion([0.0, 0.0, 0.0, 1.0])
    assert q.x == 0.0
    assert q.y == 0.0
    assert q.z == 0.0
    assert q.w == 1.0


def test_construct_from_rotation():
    rotation = Rotation.from_rotvec([0.0, 0.0, math.pi / 2])
    q = Quaternion(rotation)
    assert np.allclose(q.data, rotation.as_quat())


def test_construct_from_zero_norm_falls_back_to_identity():
    """Zero-norm quaternions can't be represented by `Rotation`, so construction should not raise."""
    q = Quaternion([0.0, 0.0, 0.0, 0.0])
    assert q.rotation.magnitude() == pytest.approx(0.0)


def test_identity_classmethod():
    q = Quaternion.identity()
    assert np.allclose(q.data, [0.0, 0.0, 0.0, 1.0])


def test_zero_classmethod():
    q = Quaternion.zero()
    assert np.allclose(q.data, [0.0, 0.0, 0.0, 0.0])


def test_data_is_cached_and_read_only():
    q = Quaternion(Rotation.from_rotvec([0.0, 0.0, math.pi / 2]))
    data = q.data
    assert data is q.data  # cached (same object on second access)
    with pytest.raises(ValueError):
        data[0] = 1.0  # read-only


def test_wxyz_round_trip():
    q = Quaternion([0.1, 0.2, 0.3, 0.9])
    wxyz = q.to_wxyz()
    q2 = Quaternion.from_wxyz(wxyz)
    assert np.allclose(q.data, q2.data)

# endregion


# region Properties and Comparisons

def test_is_identity_true_for_identity_quaternion():
    """Regression test: `is_identity()` must work even when `_data` hasn't been cached yet."""
    q = Quaternion(Rotation.identity())
    assert q.is_identity() is True or bool(q.is_identity()) is True


def test_is_identity_false_for_non_identity_quaternion():
    q = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    assert not q.is_identity()


def test_is_same_rotation_true_for_equal_quaternions():
    q1 = Quaternion([0.1, 0.2, 0.3, 0.9])
    q2 = Quaternion([0.1, 0.2, 0.3, 0.9])
    assert q1.is_same_rotation(q2)


def test_is_same_rotation_true_for_negated_quaternion():
    """A quaternion and its full negation represent the same rotation."""
    q1 = Quaternion([0.1, 0.2, 0.3, 0.9])
    q2 = Quaternion([-0.1, -0.2, -0.3, -0.9])
    assert q1.is_same_rotation(q2)


def test_is_same_rotation_false_for_different_rotations():
    """Regression test: default `atol` must be small enough to actually distinguish rotations."""
    q1 = Quaternion.from_axis_angle(Vector3([1.0, 0.0, 0.0]), 0.0)
    q2 = Quaternion.from_axis_angle(Vector3([0.0, 1.0, 0.0]), 180.0)
    assert not q1.is_same_rotation(q2)


def test_is_same_rotation_requires_quaternion_type():
    q = Quaternion.identity()
    with pytest.raises(TypeError):
        q.is_same_rotation((0.0, 0.0, 0.0, 1.0))


def test_eq_compares_rotations():
    q1 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 45.0)
    q2 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 45.0)
    assert q1 == q2


def test_len_and_iter():
    q = Quaternion([0.1, 0.2, 0.3, 0.9])
    assert len(q) == 4
    assert list(q) == pytest.approx([0.1, 0.2, 0.3, 0.9])

# endregion


# region Arithmetic

def test_norm_of_unit_quaternion_is_one():
    q = Quaternion.from_axis_angle(Vector3([1.0, 0.0, 0.0]), 37.0)
    assert q.norm() == pytest.approx(1.0)


def test_dot_with_quaternion():
    q1 = Quaternion([1.0, 2.0, 3.0, 4.0])
    q2 = Quaternion([5.0, 6.0, 7.0, 8.0])
    assert q1.dot(q2) == pytest.approx(1 * 5 + 2 * 6 + 3 * 7 + 4 * 8)


def test_dot_with_ndarray():
    q1 = Quaternion([1.0, 2.0, 3.0, 4.0])
    arr = np.array([5.0, 6.0, 7.0, 8.0])
    assert q1.dot(arr) == pytest.approx(70.0)


def test_neg():
    q = Quaternion([0.1, 0.2, 0.3, 0.9])
    neg = -q
    assert np.allclose(neg.data, [-0.1, -0.2, -0.3, -0.9])


def test_add_two_quaternions():
    q1 = Quaternion([1.0, 2.0, 3.0, 4.0])
    q2 = Quaternion([0.5, 0.5, 0.5, 0.5])
    result = q1 + q2
    assert np.allclose(result.data, [1.5, 2.5, 3.5, 4.5])


def test_radd_is_commutative():
    q1 = Quaternion([1.0, 2.0, 3.0, 4.0])
    q2 = Quaternion([0.5, 0.5, 0.5, 0.5])
    assert np.allclose((q1 + q2).data, (q2 + q1).data)


def test_scalar_multiplication_both_directions():
    q = Quaternion([1.0, 2.0, 3.0, 4.0])
    left = 2.0 * q
    right = q * 2.0
    assert np.allclose(left.data, [2.0, 4.0, 6.0, 8.0])
    assert np.allclose(right.data, [2.0, 4.0, 6.0, 8.0])


def test_quaternion_multiplication_matches_hamilton_product():
    """Regression test: `q * r` must return a proper `Quaternion`, not an object array of `Quaternion`s."""
    q = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    r = Quaternion.identity()
    result = q * r

    assert isinstance(result, Quaternion)
    assert result.data.dtype != object
    assert np.allclose(result.data, q.data)


def test_quaternion_multiplication_matches_matmul_for_unit_quaternions():
    q = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 40.0)
    r = Quaternion.from_axis_angle(Vector3([1.0, 0.0, 0.0]), 25.0)
    hamilton = q * r
    composed = q @ r
    assert np.allclose(hamilton.data, composed.data)


def test_quaternion_multiplication_is_not_commutative_in_general():
    q = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 40.0)
    r = Quaternion.from_axis_angle(Vector3([1.0, 0.0, 0.0]), 25.0)
    assert not np.allclose((q * r).data, (r * q).data)


def test_matmul_composition_order():
    """`(q1 @ q2)` should equal rotating by `q2` first, then `q1` (matches `scipy` `Rotation` composition)."""
    q1 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    q2 = Quaternion.from_axis_angle(Vector3([1.0, 0.0, 0.0]), 90.0)
    composed = q1 @ q2
    expected = Quaternion(q1.rotation * q2.rotation)
    assert np.allclose(composed.data, expected.data)


def test_rmatmul_reverses_order():
    q1 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    q2 = Quaternion.from_axis_angle(Vector3([1.0, 0.0, 0.0]), 90.0)
    # `q1.__rmatmul__(q2)` is triggered by `q2 @ q1` if `q2.__matmul__` doesn't handle `q1`; test directly instead.
    assert np.allclose(q1.__rmatmul__(q2).data, (q2 @ q1).data)


def test_abs_returns_rotation_magnitude():
    q = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 60.0, radians=False)
    assert abs(q) == pytest.approx(math.radians(60.0))


def test_inverse_composes_to_identity():
    q = Quaternion.from_axis_angle(Vector3([0.0, 1.0, 0.0]), 73.0)
    identity = q @ q.inverse()
    assert identity.is_same_rotation(Quaternion.identity())


def test_get_angle_diff_degrees():
    q1 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 0.0)
    q2 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    assert q1.get_angle_diff(q2) == pytest.approx(90.0, abs=1e-4)


def test_get_angle_diff_radians():
    q1 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 0.0)
    q2 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    assert q1.get_angle_diff(q2, radians=True) == pytest.approx(math.pi / 2, abs=1e-4)

# endregion


# region Rotation Application

def test_rotate_vector3_by_90_degrees_about_z():
    q = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    rotated = q.rotate_vector(Vector3([1.0, 0.0, 0.0]))
    assert isinstance(rotated, Vector3)
    assert np.allclose(rotated.data, [0.0, 1.0, 0.0], atol=1e-6)


def test_rotate_vector_identity_is_noop():
    q = Quaternion.identity()
    v = Vector3([1.0, 2.0, 3.0])
    rotated = q.rotate_vector(v)
    assert np.allclose(rotated.data, v.data)


def test_rotate_vector_rejects_unsupported_type():
    q = Quaternion.identity()
    with pytest.raises(TypeError):
        q.rotate_vector("not a vector")

# endregion


# region Format Conversions

def test_axis_angle_round_trip():
    original_axis = Vector3([0.0, 0.0, 1.0])
    q = Quaternion.from_axis_angle(original_axis, 47.0)
    axis, angle = q.to_axis_angle()
    assert angle == pytest.approx(47.0, abs=1e-4)
    assert np.allclose(axis.data, original_axis.data, atol=1e-6)


def test_axis_angle_of_identity_does_not_raise():
    """Regression test: dividing by a zero rotation-vector magnitude used to raise/return NaN."""
    axis, angle = Quaternion.identity().to_axis_angle()
    assert angle == pytest.approx(0.0)
    assert not np.isnan(axis.data).any()


def test_axis_helper_matches_from_axis_angle():
    q1 = Quaternion.axis([0.0, 1.0, 0.0], 30.0)
    q2 = Quaternion.from_axis_angle(Vector3([0.0, 1.0, 0.0]), 30.0)
    assert np.allclose(q1.data, q2.data)


def test_matrix3_round_trip():
    q = Quaternion.from_axis_angle(Vector3([0.0, 1.0, 0.0]), 65.0)
    matrix = q.to_matrix3()
    assert isinstance(matrix, Matrix3)
    q2 = Quaternion.from_matrix3(matrix)
    assert q.is_same_rotation(q2)


def test_matrix4_round_trip():
    q = Quaternion.from_axis_angle(Vector3([1.0, 0.0, 0.0]), 20.0)
    matrix4 = q.to_matrix4()
    q2 = Quaternion.from_matrix4(matrix4.data)
    assert q.is_same_rotation(q2)


def test_euler_angles_round_trip_degrees():
    q = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 33.0)
    euler = q.to_euler_angles_deg(order="xzy")
    q2 = Quaternion.from_euler_angles_deg(euler, order="xzy")
    assert q.is_same_rotation(q2)


def test_from_vector_change_rotates_v1_onto_v2():
    v1 = Vector3([1.0, 0.0, 0.0])
    v2 = Vector3([0.0, 1.0, 0.0])
    q = Quaternion.from_vector_change(v1, v2)
    rotated = q.rotate_vector(v1)
    assert np.allclose(rotated.data, v2.data, atol=1e-6)

# endregion


# region Quantization

def test_three_comp_40_round_trip_for_unit_quaternion():
    """`ThreeComp40` is a lossy 12-bit-per-component quantization, so allow for its quantization step size."""
    q = Quaternion.from_axis_angle(Vector3([0.3, 0.6, 0.1]), 82.0)
    encoded = q.encode_ThreeComp40()
    decoded = Quaternion.decode_ThreeComp40(encoded)
    assert q.is_same_rotation(decoded, ignore_direction=True, atol=Quaternion.THREECOMP40_STEP)


def test_three_comp_40_round_trip_for_identity():
    q = Quaternion.identity()
    encoded = q.encode_ThreeComp40()
    decoded = Quaternion.decode_ThreeComp40(encoded)
    assert q.is_same_rotation(decoded, ignore_direction=True)

# endregion


# region Slerp

def test_slerp_at_t0_returns_first_quaternion():
    q1 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 0.0)
    q2 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    result = Quaternion.slerp(q1, q2, 0.0)
    assert result.is_same_rotation(q1)


def test_slerp_at_t1_returns_second_quaternion():
    q1 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 0.0)
    q2 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    result = Quaternion.slerp(q1, q2, 1.0)
    assert result.is_same_rotation(q2)


def test_slerp_at_midpoint_is_halfway_rotation():
    q1 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 0.0)
    q2 = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 90.0)
    result = Quaternion.slerp(q1, q2, 0.5)
    expected = Quaternion.from_axis_angle(Vector3([0.0, 0.0, 1.0]), 45.0)
    assert result.is_same_rotation(expected)

# endregion
