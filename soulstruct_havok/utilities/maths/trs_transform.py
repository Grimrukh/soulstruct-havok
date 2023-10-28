from __future__ import annotations

__all__ = ["TRSTransform"]

import logging
import math
import typing as tp
from dataclasses import dataclass, field

import numpy as np

from soulstruct.utilities.maths import Vector3, Vector4, Matrix4

from .quaternion import Quaternion

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class TRSTransform:
    """Holds the translation, rotation, and scale components that define a coordinate system (e.g., a Havok bone or
    one frame or spline control point in a bone animation track).

    CANNOT represent arbitrary affine transformations -- only those with no shear component. The constructor will log a
    warning if you initialize it with non-uniform scale, as this will make the `TRSTransform` non-invertible.

    Corresponds to `hkQsTransformf` Havok type.
    """
    WARN_NONUNIFORM_SCALE: tp.ClassVar[bool] = False

    translation: Vector3 = field(default_factory=Vector3.zero)
    rotation: Quaternion = field(default_factory=Quaternion.identity)
    scale: Vector3 = field(default_factory=Vector3.one)

    def __post_init__(self):
        if self.WARN_NONUNIFORM_SCALE and (self.scale.x != self.scale.y or self.scale.x != self.scale.z):
            _LOGGER.warning(f"`TRSTransform` created with non-uniform `scale`: {self.scale}")

    def transform_vector(self, vector: Vector3 | Vector4) -> Vector3 | Vector4:
        """Apply this transform to `vector`. Returned vector will have the same length as input (3 or 4), with the
        fourth `w` element untouched for `Vector4`."""
        if isinstance(vector, Vector3):
            transformed = self.translation.data + self.rotation.rotate_vector(self.scale.data * vector.data)
            return Vector3(transformed)
        elif isinstance(vector, Vector4):
            transformed = self.translation.data + self.rotation.rotate_vector(self.scale.data * vector.data[:3])
            return Vector4(np.r_[transformed, vector.w])
        raise TypeError(f"Cannot transform vector of type {type(vector)}.")

    def transform_vector_array(self, vector_array: np.ndarray):
        """Transform each row vector in `vector_array`.

        Array must have three or four columns (fourth column will be untouched if present).
        """
        if vector_array.shape[1] == 3:
            return self.translation.data + self.rotation.rotate_vector(self.scale.data * vector_array)
        elif vector_array.shape[1] == 4:
            array3 = self.translation.data + self.rotation.rotate_vector(self.scale.data * vector_array[:, :3])
            return np.column_stack([array3, vector_array[:, 3]])
        raise ValueError(f"`vector_array` must have three or four columns (not {vector_array.shape[1]}).")

    def left_multiply_rotation(self, rotation: Quaternion):
        """Update `self.rotation` by left-multiplying it with `rotation`."""
        self.rotation = rotation @ self.rotation

    def right_multiply_rotation(self, rotation: Quaternion):
        """Update `self.rotation` by right-multiplying it with `rotation`.

        Useful for transforming a coordinate system in a way that 'corresponds' (from the perspective of some higher
        frame of reference) to LEFT-multiplying the rotation of a vector within it.
        """
        self.rotation = self.rotation @ rotation

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
            np.allclose(self.translation, [0.0, 0.0, 0.0])
            and self.rotation.is_identity()
            and np.allclose(self.scale, [1.0, 1.0, 1.0])
        )

    @classmethod
    def identity(cls) -> TRSTransform:
        """Dataclass field defaults are already set to identity."""
        return cls()

    @classmethod
    def lerp(cls, transform1: TRSTransform, transform2: TRSTransform, t: float):
        """Linearly interpolate translate and scale, and spherically interpolate rotation Quaternion.

        `t` will be clamped to [0, 1] interval.
        """
        t = min(1.0, max(0.0, t))
        translation = transform1.translation.data + (transform2.translation.data - transform1.translation.data) * t
        rotation = Quaternion.slerp(transform1.rotation, transform2.rotation, t)
        scale = transform1.scale.data + (transform2.scale.data - transform1.scale.data) * t
        return cls(Vector3(translation), rotation, Vector3(scale))

    # @profile
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
            other_translation = Vector3(self.scale.data * other.translation.data)
        else:
            other_translation = other.translation
        new_translation = self.translation.data + self.rotation.rotate_vector(other_translation.data)
        new_rotation = self.rotation @ other.rotation
        new_scale = self.scale.data * other.scale.data
        return TRSTransform(Vector3(new_translation), new_rotation, Vector3(new_scale))

    def __matmul__(self, other: TRSTransform):
        """Shortcut for `compose(other, scale_translation=True)`."""
        return self.compose(other, scale_translation=True)

    def to_matrix4(self) -> Matrix4:
        """Convert `translation` vector, `rotation` Quaternion, and `scale` vector to a 4x4 homogenous transform matrix.

        The resulting matrix is just the `T @ R @ S` composition of the three transformation types.
        """
        t_mat = Matrix4.from_translate(self.translation)
        r_mat = Matrix4.from_rotation_matrix3(self.rotation.to_matrix3())
        s_mat = Matrix4.from_scale(self.scale)
        return t_mat @ r_mat @ s_mat

    @classmethod
    def from_matrix4(cls, matrix4: np.ndarray | Matrix4) -> TRSTransform:
        """Attempt to decompose `matrix4` into translation, rotation, and scale components.

        Will raise a `ValueError` if non-zero shear is detected in `matrix4`.
        """

        if isinstance(matrix4, Matrix4):
            matrix4 = matrix4.data

        translate = matrix4[:-1, -1]
        rzs = matrix4[:-1, :-1]  # top-left 3x3  # type: np.ndarray
        rzs0, rzs1, rzs2 = rzs.T  # columns of RZS

        # Extract X scale and remove it from first column of RZS.
        scale_x = math.sqrt(np.sum(rzs0 ** 2))
        rzs0 /= scale_x

        # Orthogonalize second column of RZS with respect to scale-normalized first column.
        sx_sxy = np.dot(rzs0, rzs1)
        rzs1 -= sx_sxy * rzs0

        # Extract Y scale and remove it from second column of RZS.
        scale_y = math.sqrt(np.sum(rzs1 ** 2))
        rzs1 /= scale_y

        # Orthogonalize third column of RZS with respect to scale-normalized first two columns.
        sx_sxz = np.dot(rzs0, rzs2)
        sy_syz = np.dot(rzs1, rzs2)
        rzs2 -= sx_sxz * rzs0 + sy_syz * rzs1

        # Extract Z scale and remove it from third column of RZS.
        scale_z = math.sqrt(np.sum(rzs2 ** 2))
        rzs2 /= scale_z

        # Check that shear is zero.
        shear_xy = sx_sxy / scale_x
        shear_xz = sx_sxz / scale_x
        shear_yz = sy_syz / scale_y
        shear = [shear_xy, shear_xz, shear_yz]
        if not np.allclose(shear, 0.0):
            raise ValueError(f"Cannot convert a 4x4 matrix with non-zero shear to `TRSTransform`: {shear}")

        # Reconstruct rotation matrix and ensure determinant is positive (inverting X scale if necessary).
        rot_mat = np.column_stack([rzs0, rzs1, rzs2])
        if np.linalg.det(rot_mat) < 0:
            scale_x *= -1
            rot_mat[:, 0] *= -1

        return TRSTransform(
            translation=Vector3(translate),
            rotation=Quaternion.from_matrix3(rot_mat),
            scale=Vector3((scale_x, scale_y, scale_z)),
        )

    def __repr__(self) -> str:
        return (
            f"TRSTransform(\n"
            f"    translation={self.translation},\n"
            f"    rotation={self.rotation},\n"
            f"    scale={self.scale},\n"
            f")"
        )
