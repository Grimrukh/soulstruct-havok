from __future__ import annotations

__all__ = [
    "scale_shape",
    "scale_vector4_xyz",
    "scale_transform_translation",
    "scale_motion_state",
    "scale_constraint_data",
]

import logging
import typing as tp

from soulstruct_havok.utilities.maths import Matrix4, Vector3, Vector4

from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2018

_LOGGER = logging.getLogger(__name__)

SHAPE_TYPING = tp.Union[
    hk2010.hkpShape, hk2015.hkpShape,
]
CONVEX_SHAPE_TYPES = (
    hk2010.hkpConvexShape, hk2015.hkpConvexShape
)
CONVEX_VERTICES_SHAPE_TYPES = (
    hk2015.hkpConvexVerticesShape,
)
BOX_SHAPE_TYPES = (
    hk2015.hkpBoxShape
)
CONVEX_TRANSFORM_SHAPE_BASE_TYPES = (
    hk2015.hkpConvexTransformShapeBase
)
CONVEX_TRANSFORM_SHAPE_TYPES = (
    hk2015.hkpConvexTransformShape
)
CONVEX_TRANSLATE_SHAPE_TYPES = (
    hk2015.hkpConvexTranslateShape
)
CAPSULE_SHAPE_TYPES = (
    hk2010.hkpCapsuleShape, hk2015.hkpCapsuleShape
)
CYLINDER_SHAPE_TYPES = (
    hk2015.hkpCylinderShape
)
MOPP_BV_TREE_SHAPE_TYPES = (
    hk2015.hkpMoppBvTreeShape,
)
EXTENDED_MESH_SHAPE_TYPES = (
    hk2015.hkpExtendedMeshShape,
)
STORAGE_EXTENDED_MESH_SHAPE_TYPES = (
    hk2015.hkpStorageExtendedMeshShape,
)

MOTION_STATE_TYPING = tp.Union[
    hk2010.hkMotionState, hk2015.hkMotionState,
]
CONSTRAINT_DATA_TYPING = tp.Union[
    hk2010.hkpConstraintData,
    hk2014.hkpConstraintData,
    hk2015.hkpConstraintData,
    hk2018.hkpConstraintData,
]
RAGDOLL_CONSTRAINT_DATA_TYPES = (
    hk2010.hkpRagdollConstraintData,
    hk2014.hkpRagdollConstraintData,
    hk2015.hkpRagdollConstraintData,
    hk2018.hkpRagdollConstraintData,
)
BALL_AND_SOCKET_CONSTRAINT_DATA_TYPES = (
    hk2015.hkpBallAndSocketConstraintData,
)
BALL_SOCKET_CHAIN_DATA_TYPES = (
    hk2015.hkpBallSocketChainData,
)


# region Utility Functions
def scale_shape(shape: SHAPE_TYPING, scale_factor: float | Vector3 | Vector4):
    if isinstance(shape, MOPP_BV_TREE_SHAPE_TYPES):
        scale_shape(shape.child.childShape, scale_factor)
        return

    if isinstance(scale_factor, Vector3):
        scale_factor = Vector4.from_vector3(scale_factor)

    if isinstance(shape, CONVEX_SHAPE_TYPES):
        radius_scalar = _get_scalar_float(scale_factor, shape.__class__.__name__ + ".radius")
        shape.radius *= radius_scalar
        if isinstance(shape, BOX_SHAPE_TYPES):
            shape.halfExtents *= scale_factor
        elif isinstance(shape, CAPSULE_SHAPE_TYPES):
            shape.vertexA *= scale_factor
            shape.vertexB *= scale_factor
        elif isinstance(shape, CONVEX_TRANSFORM_SHAPE_BASE_TYPES):
            if shape.childShape and shape.childShape.childShape:  # recur on child, if present
                scale_shape(shape.childShape.childShape, scale_factor)
            if isinstance(shape, CONVEX_TRANSLATE_SHAPE_TYPES):
                shape.translation *= scale_factor
            elif isinstance(shape, CONVEX_TRANSFORM_SHAPE_TYPES):
                shape.transform.translation *= scale_factor
        elif isinstance(shape, CONVEX_VERTICES_SHAPE_TYPES):
            shape.aabbHalfExtents *= scale_factor
            shape.aabbCenter *= scale_factor
            # TODO: `rotatedVertices` is a list of `Matrix3`. I assume they are pure rotations and don't need scaling...
            shape.planeEquations = [equation * scale_factor for equation in shape.planeEquations]
        elif isinstance(shape, CYLINDER_SHAPE_TYPES):
            _LOGGER.warning("Scaled a `hkpCylinderShape` instance, but the method has not been thoroughly tested!")
            shape.cylRadius *= radius_scalar
            # TODO: Guessing that this should be scaled.
            shape.cylBaseRadiusFactorForHeightFieldCollisions *= radius_scalar
            # TODO: These vertices have a `w` component, but I don't know what it is for. Not scaling it for now.
            #  (They also seem to only have non-zero Y, which I guess makes sense for a vertical, centered cylinder.)
            shape.vertexA *= scale_factor
            shape.vertexB *= scale_factor
        return

    if isinstance(shape, EXTENDED_MESH_SHAPE_TYPES):
        shape.embeddedTrianglesSubpart.transform.translation *= scale_factor
        shape.aabbHalfExtents *= scale_factor
        shape.aabbCenter *= scale_factor
        if isinstance(shape, STORAGE_EXTENDED_MESH_SHAPE_TYPES):
            for mesh in shape.meshstorage:
                for i, vertex in enumerate(mesh.vertices):
                    mesh.vertices[i] = vertex * scale_factor
        return

    raise TypeError(f"Cannot scale Havok shape type: {type(shape).__name__}.")


def scale_vector4_xyz(vector4: Vector4, scale_factor: float | Vector3 | Vector4):
    """Scale only XYZ components of a `Vector4` in-place."""
    if isinstance(scale_factor, (Vector3, Vector4)):
        vector4.x *= scale_factor.x
        vector4.y *= scale_factor.y
        vector4.z *= scale_factor.z
    else:
        vector4.x *= scale_factor
        vector4.y *= scale_factor
        vector4.z *= scale_factor


def scale_transform_translation(transform: tuple[float], scale_factor: float | Vector3 | Vector4) -> tuple[float]:
    """Scale translation component of 16-float tuple that represents `hkTransform` or `hkTransformf` and return scaled
    tuple."""
    transform = Matrix4.from_flat_column_order(transform)
    if isinstance(scale_factor, (Vector3, Vector4)):
        transform[0, 3] *= scale_factor.x
        transform[1, 3] *= scale_factor.y
        transform[2, 3] *= scale_factor.z
    else:
        transform[0, 3] *= scale_factor
        transform[1, 3] *= scale_factor
        transform[2, 3] *= scale_factor
    return tuple(transform.to_flat_column_order())


def scale_motion_state(motion_state: MOTION_STATE_TYPING, scale_factor: float | Vector3 | Vector4):
    motion_state.transform = scale_transform_translation(motion_state.transform, scale_factor)

    radius_scalar = _get_scalar_float(scale_factor, motion_state.__class__.__name__ + ".objectRadius")
    motion_state.objectRadius *= radius_scalar

    # NOTE: In newer `hkMotionState`, the `hkSweptTransform` explicit type has been replaced with a simple tuple of
    # five `hkVector4`s, for some reason. I assume the layout is the same:
    #   centerOfMass0: Vector4
    #   centerOfMass1: Vector4
    #   rotation0: hkQuaternionf
    #   rotation1: hkQuaternionf
    #   centerOfMassLocal: Vector4

    # So we want to scale indices 0, 1, and 4 of the tuple, which are the `centerOfMass0`, `centerOfMass1`, and
    # `centerOfMassLocal` vectors.
    motion_state.sweptTransform = tuple(
        vector4 * scale_factor if i in {0, 1, 4} else vector4
        for i, vector4 in enumerate(motion_state.sweptTransform)
    )


def scale_constraint_data(constraint_data: CONSTRAINT_DATA_TYPING, scale_factor: float | Vector3 | Vector4):
    if isinstance(constraint_data, RAGDOLL_CONSTRAINT_DATA_TYPES):
        # TODO: There are a bunch of forces/constraints in here that I'm not sure how to scale.
        atoms = constraint_data.atoms
        atoms.transforms.transformA = scale_transform_translation(atoms.transforms.transformA, scale_factor)
        atoms.transforms.transformB = scale_transform_translation(atoms.transforms.transformB, scale_factor)

    elif isinstance(constraint_data, BALL_SOCKET_CHAIN_DATA_TYPES):
        constraint_scalar = _get_scalar_float(scale_factor, constraint_data.__class__.__name__ + ".maxErrorDistance")
        constraint_data.link0PivotBVelocity *= scale_factor
        constraint_data.maxErrorDistance *= constraint_scalar
        constraint_data.inertiaPerMeter *= constraint_scalar
        # TODO: tau, damping, cfm?
        for info in constraint_data.infos:
            # TODO: Possibly don't want to scale `w`.
            info.pivotInA *= scale_factor
            info.pivotInB *= scale_factor

    elif isinstance(constraint_data, BALL_AND_SOCKET_CONSTRAINT_DATA_TYPES):
        # TODO: There are a bunch of forces/constraints in here that I'm not sure how to scale.
        atoms = constraint_data.atoms
        scale_vector4_xyz(atoms.pivots.translationA, scale_factor)
        scale_vector4_xyz(atoms.pivots.translationB, scale_factor)

    # TODO: Watch out for constraint data class with `atoms.spring` (length and maxLength).

# endregion


def _get_scalar_float(value: float | Vector3 | Vector4, type_name: str) -> float:
    """Get scalar float value from `float`, `Vector3`, or `Vector4`.

    Logs a warning if `value` is a `Vector3` or `Vector4` with non-uniform components, in which case the maximum
    component is used.
    """
    if isinstance(value, (Vector3, Vector4)):
        if len(set(value[:3])) != 1:
            _LOGGER.warning(
                f"Scaling `{type_name}` with non-uniform vector: {value}. Using max component."
            )
        return max(value)
    return value
