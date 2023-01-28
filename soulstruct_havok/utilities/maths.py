"""Extends vector and matrix structures from `soulstruct` with `numpy` and `scipy` functions.

Also adds `Quaternion` structure.
"""
from __future__ import annotations

__all__ = [
    "invert_matrix",
    "Quaternion",
    "TRSTransform",
    "Vector3",
    "Vector4",
]

import logging
import math
import typing as tp

import numpy
from scipy.spatial.transform import Rotation, Slerp
from scipy.linalg import inv as scipy_inv

from soulstruct.utilities.maths import *
from soulstruct.utilities.conversion import floatify

_LOGGER = logging.getLogger(__name__)

ARRAYLIKE = tp.Union[tuple, list, numpy.ndarray, Vector3, Vector4]


def invert_matrix(matrix: numpy.ndarray):
    return scipy_inv(matrix)


class Quaternion:
    """Provides some basic wrapper constructors and methods for a 4-element float array representing a quaternion.

    This is the predominant rotation format used by Havok (unlike regular FromSoft game files, which generally use
    XZY Euler angles). Uses `scipy` `Rotation` methods to convert to and from other rotation formats, but does not
    expose the `Rotation` class directly.

    Stores the real component `w` last, as Havok does (and `scipy`, conveniently).
    """
    THREECOMP40_START = -math.sqrt(2) / 2  # -0.7071067811865476
    THREECOMP40_STEP = math.sqrt(2) / 4095  # 0.00034535129728280713
    _IDENTITY = [0.0, 0.0, 0.0, 1.0]

    data: list[float, float, float, float]

    def __init__(self, x: float | ARRAYLIKE | Quaternion, y: float = None, z: float = None, w: float = None):
        if y is None and z is None and w is None:
            x, y, z, w = x
        elif y is None or z is None or w is None:
            raise ValueError("Quaternion must be constructed with a four-element array or four separate arguments.")
        self.data = [x, y, z, w]

    @property
    def x(self):
        return self.data[0]

    @property
    def y(self):
        return self.data[1]

    @property
    def z(self):
        return self.data[2]

    @property
    def w(self):
        return self.data[3]

    real = w

    def imag(self) -> Vector3:
        return Vector3(*self.data[:3])

    def rotate_vector(self, vector: Vector3 | Vector4) -> Vector3 | Vector4:
        if isinstance(vector, Vector3):
            return Vector3(*Rotation.from_quat(self.data).apply(vector._data))
        return Vector4(*Rotation.from_quat(self.data).apply(vector._data))

    def __getitem__(self, index: int) -> float:
        if index < 0 or index > 3:
            raise ValueError("Quaternion index must be between 0-3.")
        return self.data[index]

    def __setitem__(self, index: int, value: float):
        if index < 0 or index > 3:
            raise ValueError("Quaternion index must be between 0-3.")
        self.data[index] = value

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        """Should always be 4, but confirming just in case."""
        return len(self.data)

    def __eq__(self, other: Quaternion):
        if isinstance(other, Quaternion):
            return all(math.isclose(self.data[i], other.data[i], rel_tol=1.e-5, abs_tol=1.e-8) for i in range(4))
        raise TypeError("Can only compare equality for `Quaternion` with another `Quaternion`.")

    def normalize(self) -> Quaternion:
        magnitude = abs(self)
        return Quaternion([v / magnitude for v in self.data])

    @classmethod
    def from_wxyz(cls, w: float | ARRAYLIKE | Quaternion, x: float = None, y: float = None, z: float = None):
        if x is None and y is None and z is None:
            w, x, y, z = w
        elif x is None or y is None or z is None:
            raise ValueError("Quaternion must be constructed with a four-element array or four separate arguments.")
        return cls(x, y, z, w)

    def to_wxyz(self) -> list[float, float, float, float]:
        return [self.data[3], self.data[0], self.data[1], self.data[2]]

    def is_identity(self) -> bool:
        return all(math.isclose(self.data[i], self._IDENTITY[i], rel_tol=1.e-5, abs_tol=1.3 - 8) for i in range(4))

    @classmethod
    def identity(cls) -> Quaternion:
        return Quaternion(0.0, 0.0, 0.0, 1.0)

    @classmethod
    def zero(cls) -> Quaternion:
        return Quaternion(0.0, 0.0, 0.0, 0.0)

    @classmethod
    def from_vector_change(cls, v1: Vector3, v2: Vector3):
        """Get `Quaternion` representing the rotation from `v1` to `v2`."""
        dot = v1.dot(v2)
        xyz = v1.cross(v2)
        w = math.sqrt(v1.get_squared_magnitude() * v2.get_squared_magnitude()) + dot
        return cls(*xyz, w).normalize()

    def inverse(self) -> Quaternion:
        return Quaternion(self.R.inv().as_quat())

    # TODO: conjugate? Not needed yet.

    # region Format Conversions
    @classmethod
    def from_matrix3(cls, matrix3: numpy.ndarray | Matrix3):
        if isinstance(matrix3, Matrix3):
            matrix3 = numpy.array(matrix3.data)
        return Quaternion(Rotation.from_matrix(matrix3).as_quat())

    def to_matrix3(self) -> Matrix3:
        return Matrix3.from_nested_lists(self.R.as_matrix().tolist())

    @classmethod
    def from_matrix4(cls, matrix4: numpy.ndarray | Matrix4):
        if isinstance(matrix4, Matrix4):
            matrix4 = numpy.array(matrix4.data)
        matrix3 = matrix4[:3, :3]  # top-left 3x3
        return Quaternion(Rotation.from_matrix(matrix3).as_quat())

    def to_matrix4(self) -> Matrix4:
        matrix3 = Matrix3.from_nested_lists(self.R.as_matrix().tolist())
        return Matrix4.from_rotation_matrix3(matrix3)

    @classmethod
    def from_axis_angle(cls, axis: Vector3, angle: float, radians=False) -> Quaternion:
        if not radians:
            angle = math.radians(angle)
        return Quaternion(Rotation.from_rotvec(angle * axis).as_quat())

    def to_axis_angle(self, radians=False) -> tuple[Vector3, float]:
        rotvec = self.R.as_rotvec()
        magnitude = math.sqrt(sum(x ** 2 for x in rotvec))
        return Vector3(*(rotvec / magnitude)), (magnitude if radians else math.degrees(magnitude))

    @classmethod
    def axis(cls, x: float, y: float, z: float, angle: float, radians=False) -> Quaternion:
        """Shorter wrapper for the above."""
        return cls.from_axis_angle(Vector3(x, y, z), angle, radians)

    def to_euler_angles(self, radians=False) -> Vector3:
        mat = Matrix3.from_nested_lists(self.to_matrix3())
        return mat.to_euler_angles(radians=radians)

    @property
    def R(self):
        """Shortcut for converting to `scipy` `Rotation`."""
        return Rotation.from_quat(self.data)
    # endregion

    # region Arithmetic

    def dot(self, other: Quaternion | numpy.ndarray) -> Quaternion:
        """Simple element-wise multiplication."""
        if isinstance(other, Quaternion):
            return Quaternion(*[self.data[i] * other.data[i] for i in range(4)])
        raise TypeError(f"Cannot dot-product Quaternion with {type(other).__name__}.")

    def __add__(self, other: Quaternion | float) -> Quaternion:
        if isinstance(other, Quaternion):
            return Quaternion(*[v + o for v, o in zip(self.data, other.data)])
        elif isinstance(other, float):
            return Quaternion(*[v + other for v in self.data])
        raise TypeError(f"Cannot left-add Quaternion with {type(other).__name__}.")

    __radd__ = __add__

    def __mul__(self, other: Quaternion | float) -> Quaternion:
        """Equivalent to composing the rotation matrices."""
        if isinstance(other, Quaternion):
            other_rot = Rotation.from_quat(other.data)
            return Quaternion((self.R * other_rot).as_quat())
        elif isinstance(other, float):
            return Quaternion(*[v * other for v in self.data])
        raise TypeError(f"Cannot left-multiply Quaternion with {type(other).__name__}.")

    def __rmul__(self, other: Quaternion) -> Quaternion:
        if isinstance(other, Quaternion):
            return other.__mul__(self)
        elif isinstance(other, float):
            return Quaternion(*[v * other for v in self.data])
        raise TypeError(f"Cannot right-multiply Quaternion with {type(other).__name__}.")

    def __abs__(self) -> float:
        return self.R.magnitude()

    # endregion

    # region Quantization
    @classmethod
    def decode_Polar32(cls, c_val: int) -> Quaternion:
        r_mask = (1 << 10) - 1
        r_frac = 1.0 / r_mask
        phi_frac = math.pi / 4 / 511.0

        r = floatify((c_val >> 18) & (r_mask & 0xFFFFFFFF)) * r_frac
        r = 1.0 - (r ** 2)

        phi_theta = float(c_val & 0x3FFFF)
        phi = float(math.floor(math.sqrt(phi_theta)))
        theta = 0

        if phi > 0.0:
            theta = (math.pi / 4) * (phi_theta - (phi * phi)) / phi
            phi = phi_frac * phi

        magnitude = float(math.sqrt(1.0 - (r ** 2)))

        q = [
            math.sin(phi) * math.cos(theta) * magnitude,
            math.sin(phi) * math.sin(theta) * magnitude,
            math.cos(phi) * magnitude,
            r,
        ]

        if (c_val & 0x10000000) > 0:
            q[0] *= -1
        if (c_val & 0x20000000) > 0:
            q[1] *= -1
        if (c_val & 0x40000000) > 0:
            q[2] *= -1
        if (c_val & 0x80000000) > 0:
            q[3] *= -1

        return cls(*q)

    @classmethod
    def decode_ThreeComp48(cls, x: int, y: int, z: int) -> Quaternion:
        mask = (1 << 15) - 1
        fractal = 0.000043161

        result_shift = ((y >> 14) & 2) | ((x >> 15) & 1)
        r_sign = (z >> 15) != 0

        x &= mask
        x -= mask >> 1
        y &= mask
        y -= mask >> 1
        z &= mask
        z -= mask >> 1

        temp_val = (x * fractal, y * fractal, z * fractal)

        float_value = [math.nan] * 4
        for i in range(4):
            if i < result_shift:
                float_value[i] = temp_val[i]
            elif i == result_shift:
                t = 1.0 - temp_val[0] * temp_val[0] - temp_val[1] * temp_val[1] - temp_val[2] * temp_val[2]
                float_value[i] = (0.0 if t <= 0.0 else math.sqrt(t)) * (-1 if r_sign else 1)
            elif i > result_shift:
                float_value[i] = temp_val[i - 1]

        return Quaternion(*float_value)

    @classmethod
    def decode_ThreeComp40(cls, c_val: int) -> Quaternion:
        mask = (1 << 12) - 1  # twelve 1-bits (4095)
        v0 = c_val & mask  # lowest twelve bits
        v1 = (c_val >> 12) & mask  # next twelve bits
        v2 = (c_val >> 24) & mask  # next twelve bits
        implicit_dimension = (c_val >> 36) & 0b0011  # next two bits
        implicit_negative = ((c_val >> 38) & 1) > 0  # final two bits

        # Multiply masked values by fractal to convert to [-sqrt(2), sqrt(2)] range.
        q = [cls.THREECOMP40_START + v * cls.THREECOMP40_STEP for v in (v0, v1, v2)]  # still missing implicit dimension

        # Calculate implicit dimension from unit magnitude.
        # The implicit dimension is always the one with the largest absolute value (outside the +/- sqrt(2) range).
        implicit_squared = 1.0 - q[0] ** 2 - q[1] ** 2 - q[2] ** 2
        # Clamp to zero (means this was NOT a unit quaternion!) or square root.
        implicit = 0.0 if implicit_squared <= 0.0 else math.sqrt(implicit_squared)
        # Apply sign.
        if implicit_negative:
            implicit *= -1
        # Insert implicit dimension.
        q.insert(implicit_dimension, implicit)
        return cls(*q)

    def encode_ThreeComp40(self) -> int:
        """Encode Quaternion into a 40-bit (five-byte) integer. Most common quantization used in FromSoft splines."""
        mask = (1 << 12) - 1  # twelve 1-bits (4095)
        implicit_dimension = self.data.index(max(self.data))
        implicit_negative = int(self.data[implicit_dimension] < 0)

        encoded_floats = []  # type: list[int]
        for i in range(4):
            if i == implicit_dimension:
                continue  # skipped
            encoded = round((self.data[i] - self.THREECOMP40_START) / self.THREECOMP40_STEP)  # int between 0 and 4095
            encoded_floats.append(encoded)

        # Join everything together.
        c_val = encoded_floats[0] & mask
        c_val += (encoded_floats[1] & mask) << 12
        c_val += (encoded_floats[2] & mask) << 24
        c_val += implicit_dimension << 36
        c_val += implicit_negative << 38

        return c_val
    # endregion

    def __repr__(self) -> str:
        return f"Quaternion(x={self.data[0]:.4f}, y={self.data[1]:.4f}, z={self.data[2]:.4f}, w={self.data[3]:.4f})"

    @staticmethod
    def slerp(q1: Quaternion, q2: Quaternion, t: float) -> Quaternion:
        """Spherically interpolate between two Quaternions by parameter `t` in interval [0, 1].
        """
        scipy_slerp = Slerp([0, 1], Rotation.concatenate([q1.R, q2.R]))
        return Quaternion(scipy_slerp(t).as_quat())


class TRSTransform:
    """Holds the translation, rotation, and scale components that define a coordinate system (e.g., a Havok bone or
    one frame or spline control point in a bone animation track).

    CANNOT represent arbitrary affine transformations -- only those with no shear component. The constructor will log a
    warning if you initialize it with non-uniform scale, as this will make the `TRSTransform` non-invertible.

    Corresponds to `hkQsTransformf` Havok type.
    """
    WARN_NONUNIFORM_SCALE = False

    translation: Vector3
    rotation: Quaternion
    scale: Vector3

    def __init__(
        self,
        translation: tp.Union[Vector3, Vector4, list, tuple] = None,
        rotation: Quaternion = None,
        scale: tp.Union[float, Vector3, Vector4] = None,
    ):
        self.translation = Vector3(*translation) if translation is not None else Vector3.zero()
        self.rotation = Quaternion(rotation) if rotation is not None else Quaternion.identity()
        if scale is None:
            self.scale = Vector3.ones()
        elif isinstance(scale, (int, float)):
            self.scale = float(scale) * Vector3.ones()
        else:
            self.scale = Vector3(*scale)
            if self.WARN_NONUNIFORM_SCALE and (self.scale.x != self.scale.y or self.scale.x != self.scale.z):
                _LOGGER.warning(f"`TRSTransform` created with non-uniform scale: {self.scale}")

    def transform_vector(self, vector: Vector3 | Vector4) -> Vector3 | Vector4:
        """Apply this transform to `vector`. Returned vector will have the same length as input (3 or 4), with the
        fourth element untouched for `Vector4`."""
        transformed = self.translation + self.rotation.rotate_vector(self.scale * Vector3(*vector))
        if isinstance(vector, Vector4):
            return Vector4(*transformed, vector.w)
        return transformed

    def left_multiply_rotation(self, rotation: Quaternion):
        """Update `self.rotation` by left-multiplying it with `rotation`."""
        self.rotation = rotation * self.rotation

    def right_multiply_rotation(self, rotation: Quaternion):
        """Update `self.rotation` by right-multiplying it with `rotation`.

        Useful for transforming a coordinate system in a way that corresponds to LEFT-multiplying the rotation of a
        vector within it.
        """
        self.rotation = self.rotation * rotation

    def inverse_transform_vector(self, vector: Vector3 | Vector4) -> Vector3 | Vector4:
        """Apply the INVERSE of this transform to `vector`. Last element is ignored for `Vector4`s."""
        return self.inverse().transform_vector(vector)

    def inverse(self) -> TRSTransform:
        """Get the inverse transform.

        Even if scale is non-uniform, this will always produce a `TRSTransform` that is the inverse of the `compose`
        function that defines `TRSTransform` multiplication. This inversion operation does NOT correspond to affine
        matrix inversion if scale is non-uniform!
        """
        inv_translation = -self.rotation.inverse().rotate_vector(self.translation)
        inv_rotation = self.rotation.inverse()
        inv_scale = 1.0 / self.scale
        return TRSTransform(inv_translation, inv_rotation, inv_scale)

    def copy(self) -> TRSTransform:
        return TRSTransform(self.translation, self.rotation, self.scale)

    def is_identity(self) -> bool:
        return (
            numpy.allclose(self.translation, [0, 0, 0])
            and numpy.allclose(self.rotation, [0, 0, 0, 1])
            and numpy.allclose(self.scale, [1, 1, 1])
        )

    @classmethod
    def identity(cls) -> TRSTransform:
        return cls(
            Vector3.zero(),
            Quaternion.identity(),
            Vector3.ones(),
        )

    @classmethod
    def lerp(cls, transform1: TRSTransform, transform2: TRSTransform, t: float):
        """Linearly interpolate translate and scale, and spherically interpolate rotation Quaternion.

        `t` will be clamped to [0, 1] interval.
        """
        t = min(1.0, max(0.0, t))
        translation = transform1.translation + (transform2.translation - transform1.translation) * t
        rotation = Quaternion.slerp(transform1.rotation, transform2.rotation, t)
        scale = transform1.scale + (transform2.scale - transform1.scale) * t
        return cls(translation, rotation, scale)

    def compose(self, other: TRSTransform, scale_translation=False) -> TRSTransform:
        """Combine two `TRSTransforms`.

        We cannot rely on general composition of affine transformations (e.g., 4x4 matrix multiplication) to compose
        `TRSTransform`s because they can only represent a subset of affine transformations (those without shear). The
        caller must decide how to resolve this.

        If `scale_translation=True`, then this (left) transform's scale will be applied to the other (right) transform's
        translation before rotation. This represents a proper composition, with:
            T' = R1 * S1 * T2 + T1
        Otherwise (by default), scale will NOT be applied to the translation -- just rotation. That is:
            T' = R1 * T2 + T1
        In both cases:
            R' = R1 * R2 (Quaternion multiplication == 3x3 rotation matrix composition)
            S' = S1 * S2 (element-wise vector multiplication)

        Fortunately, issues will only arise in cases of non-uniform scaling, which you are NOT recommended to use, as
        their inverse transformations will have non-zero shear. Among other things, this will make it difficult to
        make certain spatial bone corrections, as you will not be able to construct accurate frame transforms from
        inversions.

        The `TRSTransform` constructor will log a warning if you initialize it with non-uniform scale.
        """
        if not isinstance(other, TRSTransform):
            raise TypeError("Can only compose `TRSTransform` with another `TRSTransform`.")
        if scale_translation:
            new_translation = self.translation + self.rotation.rotate_vector(self.scale * other.translation)
        else:
            new_translation = self.translation + self.rotation.rotate_vector(other.translation)
        new_rotation = self.rotation * other.rotation
        new_scale = self.scale * other.scale
        return TRSTransform(new_translation, new_rotation, new_scale)

    def __matmul__(self, other: TRSTransform):
        """Shortcut for `compose(other, scale_translation=True)`."""
        return self.compose(other, scale_translation=True)

    def to_matrix4(self) -> Matrix4:
        """Convert `translate` vector, `rotation` quaternion, and `scale` vector to a 4x4 transform matrix.

        The resulting matrix is just the `T @ R @ S` composition of the three transformation types.
        """
        t_mat = Matrix4.from_translate(self.translation)
        r_mat = Matrix4.from_rotation_matrix3(self.rotation.to_matrix3())
        s_mat = Matrix4.from_scale(self.scale)
        return t_mat @ r_mat @ s_mat

    @classmethod
    def from_matrix4(cls, matrix4: numpy.ndarray | Matrix4) -> TRSTransform:
        """Attempt to decompose `matrix4` into translation, rotation, and scale components.

        Will raise a `ValueError` if non-zero shear is detected in `matrix4`.
        """

        if isinstance(matrix4, Matrix4):
            matrix4 = numpy.array(matrix4.data)

        translate = matrix4[:-1, -1]
        rzs = matrix4[:-1, :-1]  # top-left 3x3  # type: numpy.ndarray
        rzs0, rzs1, rzs2 = rzs.T  # columns of RZS

        # Extract X scale and remove it from first column of RZS.
        scale_x = math.sqrt(numpy.sum(rzs0 ** 2))
        rzs0 /= scale_x

        # Orthogonalize second column of RZS with respect to scale-normalized first column.
        sx_sxy = numpy.dot(rzs0, rzs1)
        rzs1 -= sx_sxy * rzs0

        # Extract Y scale and remove it from second column of RZS.
        scale_y = math.sqrt(numpy.sum(rzs1 ** 2))
        rzs1 /= scale_y

        # Orthogonalize third column of RZS with respect to scale-normalized first two columns.
        sx_sxz = numpy.dot(rzs0, rzs2)
        sy_syz = numpy.dot(rzs1, rzs2)
        rzs2 -= sx_sxz * rzs0 + sy_syz * rzs1

        # Extract Z scale and remove it from third column of RZS.
        scale_z = math.sqrt(numpy.sum(rzs2 ** 2))
        rzs2 /= scale_z

        # Check that shear is zero.
        shear_xy = sx_sxy / scale_x
        shear_xz = sx_sxz / scale_x
        shear_yz = sy_syz / scale_y
        shear = [shear_xy, shear_xz, shear_yz]
        if not numpy.allclose(shear, 0.0):
            raise ValueError(f"Cannot convert a 4x4 matrix with non-zero shear to `TRSTransform`: {shear}")

        # Reconstruct rotation matrix and ensure determinant is positive (inverting X scale if necessary).
        rot_mat = numpy.column_stack([rzs0, rzs1, rzs2])
        if numpy.linalg.det(rot_mat) < 0:
            scale_x *= -1
            rot_mat[:, 0] *= -1

        return TRSTransform(
            translation=Vector3(*translate),
            rotation=Quaternion.from_matrix3(rot_mat),
            scale=Vector3(scale_x, scale_y, scale_z),
        )

    def __repr__(self) -> str:
        return (
            f"TRSTransform(\n"
            f"    translation={self.translation},\n"
            f"    rotation={self.rotation},\n"
            f"    scale={self.scale},\n"
            f")"
        )
