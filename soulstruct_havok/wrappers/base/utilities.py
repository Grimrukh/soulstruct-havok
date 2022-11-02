import typing as tp

from soulstruct_havok.utilities.maths import Matrix4, Vector4

from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2018

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
CONVEX_TRANSLATE_SHAPE_TYPES = (
    hk2015.hkpConvexTranslateShape
)
CAPSULE_SHAPE_TYPES = (
    hk2010.hkpCapsuleShape, hk2015.hkpCapsuleShape
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
def scale_shape(shape: SHAPE_TYPING, factor: float):
    if isinstance(shape, CONVEX_SHAPE_TYPES):
        shape.radius *= factor
        if isinstance(shape, BOX_SHAPE_TYPES):
            shape.halfExtents *= factor
        elif isinstance(shape, CAPSULE_SHAPE_TYPES):
            shape.vertexA *= factor
            shape.vertexB *= factor
        elif isinstance(shape, CONVEX_TRANSLATE_SHAPE_TYPES):
            shape.translation *= factor
        elif isinstance(shape, CONVEX_VERTICES_SHAPE_TYPES):
            shape.aabbHalfExtents *= factor
            shape.aabbCenter *= factor
            # TODO: `rotatedVertices` is a list of `Matrix3`. I assume they are pure rotations and don't need scaling...
            shape.planeEquations = [equation * factor for equation in shape.planeEquations]
    elif isinstance(shape, MOPP_BV_TREE_SHAPE_TYPES):
        scale_shape(shape.child.childShape, factor)
    elif isinstance(shape, EXTENDED_MESH_SHAPE_TYPES):
        shape.embeddedTrianglesSubpart.transform.translation *= factor
        shape.aabbHalfExtents *= factor
        shape.aabbCenter *= factor
        if isinstance(shape, STORAGE_EXTENDED_MESH_SHAPE_TYPES):
            for mesh in shape.meshstorage:
                for vertex in mesh.vertices:
                    vertex *= factor
    else:
        raise TypeError(f"Cannot scale Havok shape type: {type(shape).__name__}.")


def scale_vector4_xyz(vector4: Vector4, factor: float) -> Vector4:
    """Scale only XYZ components of a `Vector4`. Returns a copy."""
    return Vector4(
        vector4.x * factor,
        vector4.y * factor,
        vector4.z * factor,
        vector4.w,
    )


def scale_transform_translation(transform: tuple[float], factor: float) -> tuple[float]:
    """Scale translation component of 16-float tuple that represents `hkTransform` or `hkTransformf` and return scaled
    tuple."""
    transform = Matrix4.from_flat_column_order(transform)
    transform[0, 3] *= factor  # x
    transform[1, 3] *= factor  # y
    transform[2, 3] *= factor  # z
    return tuple(transform.to_flat_column_order())


def scale_motion_state(motion_state: MOTION_STATE_TYPING, factor: float):
    motion_state.transform = scale_transform_translation(motion_state.transform, factor)
    motion_state.objectRadius *= factor

    # Indices 2 and 3 are rotations.
    motion_state.sweptTransform = tuple(
        t * factor if i in {0, 1, 4} else t
        for i, t in enumerate(motion_state.sweptTransform)
    )


def scale_constraint_data(constraint_data: CONSTRAINT_DATA_TYPING, factor: float):
    if isinstance(constraint_data, RAGDOLL_CONSTRAINT_DATA_TYPES):
        # TODO: There are a bunch of forces/constraints in here that I'm not sure how to scale.
        atoms = constraint_data.atoms
        atoms.transforms.transformA = scale_transform_translation(atoms.transforms.transformA, factor)
        atoms.transforms.transformB = scale_transform_translation(atoms.transforms.transformB, factor)

    elif isinstance(constraint_data, BALL_SOCKET_CHAIN_DATA_TYPES):
        constraint_data.link0PivotBVelocity *= factor
        constraint_data.maxErrorDistance *= factor
        constraint_data.inertiaPerMeter *= factor
        # TODO: tau, damping, cfm?
        for info in constraint_data.infos:
            # TODO: Possibly don't want to scale `w`.
            info.pivotInA *= factor
            info.pivotInB *= factor

    elif isinstance(constraint_data, BALL_AND_SOCKET_CONSTRAINT_DATA_TYPES):
        # TODO: There are a bunch of forces/constraints in here that I'm not sure how to scale.
        atoms = constraint_data.atoms
        atoms.pivots.translationA = scale_vector4_xyz(atoms.pivots.translationA, factor)
        atoms.pivots.translationB = scale_vector4_xyz(atoms.pivots.translationB, factor)

    # TODO: Watch out for constraint data class with `atoms.spring` (length and maxLength).

# endregion
