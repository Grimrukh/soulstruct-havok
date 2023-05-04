from __future__ import annotations

__all__ = ["Quaternion"]

import logging
import math
import typing as tp
from dataclasses import dataclass, field

import numpy as np
from scipy.spatial.transform import Rotation, Slerp

from soulstruct.utilities.maths import Vector3, Vector4, Matrix3, Matrix4
from soulstruct.utilities.conversion import floatify

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class Quaternion:
    """Provides some basic wrapper constructors and methods for a 4-element float array representing a quaternion.

    Instances are immutable, as it is rare that they would need to be changed, and this makes it easier to store the
    4-element array as a tuple (which is immutable) for reading and printing.

    This is the predominant rotation format used by Havok (unlike regular FromSoft game files, which generally use
    XZY-order Euler angles).

    Stored internally as a `scipy` `Rotation`, as this is the most efficient way to perform arithmetic and conversions.

    NOTE: Conveniently, both Havok and `scipy` use the same order for quaternions: [x, y, z, w], with the real part (w)
    last.
    """
    THREECOMP40_START: tp.ClassVar[float] = -math.sqrt(2) / 2  # -0.7071067811865476
    THREECOMP40_STEP: tp.ClassVar[float] = math.sqrt(2) / 4094  # 0.000345435652753565 (2047 => 0.0, 4094 => sqrt(2)/2)

    rotation: Rotation = field(default_factory=Rotation.identity)
    _data: np.ndarray = None

    def __init__(self, xyzw: np.ndarray | list | tuple | Vector4 | Quaternion | Rotation):
        if isinstance(xyzw, Rotation):
            object.__setattr__(self, "rotation", xyzw)
            object.__setattr__(self, "_data", None)  # will be generated on first access
        else:
            object.__setattr__(self, "_data", np.array(xyzw))  # could be zero-norm
            try:
                object.__setattr__(self, "rotation", Rotation.from_quat(xyzw))
            except ValueError:
                # TODO: Spline control points with weight zeroes can produce zero-norm quaternions, which `Rotation`
                #  cannot handle. But will this getaround (zero ==> identity) affect slerping?
                object.__setattr__(self, "rotation", Rotation.identity())

    @classmethod
    def from_wxyz(cls, wxyz: list | tuple | Vector4 | Quaternion) -> Quaternion:
        return cls([wxyz[1], wxyz[2], wxyz[3], wxyz[0]])

    @property
    def data(self):
        """Returns the quaternion as a tuple of 4 floats. Cached on first access."""
        if self._data is None:
            object.__setattr__(self, "_data", self.rotation.as_quat())
        return self._data

    def get_real(self) -> float:
        return self.data[3]

    def get_imag(self) -> tuple[float, float, float]:
        return self.data[:3]

    @property
    def x(self) -> float:
        return self.data[0]

    @property
    def y(self) -> float:
        return self.data[1]

    @property
    def z(self) -> float:
        return self.data[2]

    @property
    def w(self) -> float:
        return self.data[3]

    def rotate_vector(self, vector: np.ndarray | Vector3 | Vector4) -> np.ndarray | Vector3 | Vector4:
        if isinstance(vector, Vector3):
            return Vector3(self.rotation.apply(vector.data))
        elif isinstance(vector, Vector4):
            return Vector4(self.rotation.apply(vector.data))
        elif isinstance(vector, np.ndarray):
            return self.rotation.apply(vector.data)  # length not checked but will cause issues if not 3 or 4
        raise TypeError(f"Can only rotate `Vector3` or `Vector4` with `Quaternion`, not {type(vector)}.")

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return 4

    def __eq__(self, other: Quaternion):
        if isinstance(other, Quaternion):
            return self.rotation == other.rotation
        raise TypeError("Can only compare equality for `Quaternion` with another `Quaternion`.")

    def to_wxyz(self) -> tuple[float, float, float, float]:
        return self.w, self.x, self.y, self.z

    def is_identity(self) -> bool:
        return np.equal(self._data, [0.0, 0.0, 0.0, 1.0]).all()

    @classmethod
    def identity(cls) -> Quaternion:
        return Quaternion(Rotation.identity())

    @classmethod
    def zero(cls) -> Quaternion:
        return Quaternion([0.0, 0.0, 0.0, 0.0])

    @classmethod
    def from_vector_change(cls, v1: Vector3, v2: Vector3):
        """Get `Quaternion` representing the rotation from `v1` to `v2`."""
        dot = v1.dot(v2)
        xyz = v1.cross(v2)
        w = math.sqrt(v1.get_squared_magnitude() * v2.get_squared_magnitude()) + dot
        magnitude = math.sqrt(sum(x ** 2 for x in xyz) + w ** 2)
        return cls([x / magnitude for x in xyz] + [w / magnitude])

    def inverse(self) -> Quaternion:
        return Quaternion(self.rotation.inv())

    # TODO: conjugate? Not needed yet.

    # region Format Conversions
    @classmethod
    def from_matrix3(cls, matrix3: np.ndarray | Matrix3):
        if isinstance(matrix3, Matrix3):
            matrix3 = matrix3.data
        return Quaternion(Rotation.from_matrix(matrix3))

    def to_matrix3(self) -> Matrix3:
        return Matrix3(self.rotation.as_matrix())

    @classmethod
    def from_matrix4(cls, matrix4: np.ndarray | Matrix4) -> Quaternion:
        matrix3 = matrix4[:3, :3]  # top-left 3x3 rotation submatrix
        return cls(Rotation.from_matrix(matrix3))

    def to_matrix4(self) -> Matrix4:
        matrix3 = Matrix3(self.rotation.as_matrix())
        return Matrix4.from_rotation_matrix3(matrix3)

    @classmethod
    def from_axis_angle(cls, axis: Vector3, angle: float, radians=False) -> Quaternion:
        if not radians:
            angle = math.radians(angle)
        return cls(Rotation.from_rotvec((angle * axis).data))

    def to_axis_angle(self, radians=False) -> tuple[Vector3, float]:
        rotvec = self.rotation.as_rotvec()
        magnitude = math.sqrt(sum(x ** 2 for x in rotvec))
        return Vector3((rotvec / magnitude)), (magnitude if radians else math.degrees(magnitude))

    @classmethod
    def axis(cls, xyz: tp.Sequence[float], angle: float, radians=False) -> Quaternion:
        """Shorter wrapper for the above."""
        return cls.from_axis_angle(Vector3(xyz), angle, radians)

    def to_euler_angles(self, radians=False, order="xzy") -> Vector3:
        """Decompose Quaternion (via Matrix3 representation) into Euler angles.

        NOTE: Can only decompose in 'xzy' order right now and will raise an error if the order is not 'xzy'.
        """
        return self.to_matrix3().to_euler_angles(radians=radians, order=order)

    # endregion

    # region Arithmetic

    def dot(self, other: Quaternion | np.ndarray) -> Quaternion:
        """Simple element-wise multiplication."""
        return Quaternion([self.data[i] * other.data[i] for i in range(4)])

    def __add__(self, other: Quaternion | float) -> Quaternion:
        """Simple element-wise addition."""
        return Quaternion([self.data[i] + other.data[i] for i in range(4)])

    __radd__ = __add__  # commutative

    def __mul__(self, other: float):
        """Scalar multiplication."""
        return Quaternion([v * other for v in self.data])

    __rmul__ = __mul__  # commutative

    def __matmul__(self, other: Quaternion) -> Quaternion:
        """Equivalent to composing the rotation matrices."""
        return Quaternion(self.rotation * other.rotation)

    def __rmatmul__(self, other: Quaternion) -> Quaternion:
        """Equivalent to composing the rotation matrices (in reverse order to `__matmul__`)."""
        return Quaternion(other.rotation * self.rotation)

    def __abs__(self) -> float:
        return self.rotation.magnitude()

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

        return cls(q)

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

        return Quaternion(float_value)

    @classmethod
    def decode_ThreeComp40(cls, c_val: int) -> Quaternion:
        mask = (1 << 12) - 1  # twelve 1-bits (4095)
        v0 = c_val & mask  # lowest twelve bits
        v1 = (c_val >> 12) & mask  # next twelve bits
        v2 = (c_val >> 24) & mask  # next twelve bits
        implicit_dimension = (c_val >> 36) & 0b0011  # next two bits
        implicit_negative = ((c_val >> 38) & 1) > 0  # final two bits

        # Scale masked values to convert to [-sqrt(2), sqrt(2)] range.
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
        return cls(q)

    def encode_ThreeComp40(self) -> int:
        """Encode Quaternion into a 40-bit (five-byte) integer. Most common quantization used in FromSoft splines."""
        mask = (1 << 12) - 1  # twelve 1-bits (4095)
        quat = self.rotation.as_quat()
        implicit_dimension = np.abs(quat).argmax()
        implicit_negative = int(quat[implicit_dimension] < 0)

        encoded_floats = []  # type: list[int]
        for i in range(4):
            if i == implicit_dimension:
                continue  # skipped
            encoded = round((quat[i] - self.THREECOMP40_START) / self.THREECOMP40_STEP)  # int between 0 and 4095
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
        quat = self.data
        return f"Quaternion(x={quat[0]:.4f}, y={quat[1]:.4f}, z={quat[2]:.4f}, w={quat[3]:.4f})"

    @staticmethod
    def slerp(q1: Quaternion, q2: Quaternion, t: float) -> Quaternion:
        """Spherically interpolate between two Quaternions by parameter `t` in interval [0, 1].

        NOTE: As `Rotation` cannot hold zero-norm quaternions -- but we sometimes need to slerp with these -- the
        `data` representation is used.
        """
        # print(q1.data, q2.data)
        scipy_slerp = Slerp([0, 1], Rotation.concatenate([Rotation.from_quat(q1.data), Rotation.from_quat(q2.data)]))
        return Quaternion(scipy_slerp(t))
