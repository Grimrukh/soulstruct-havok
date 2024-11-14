import typing as tp

__all__ = [
    "QS_TRANSFORM",
    "ANIMATION_CONTAINER_T",
    "ANIMATION_T",
    "ANIMATION_BINDING_T",
    "INTERLEAVED_ANIMATION_T",
    "SPLINE_ANIMATION_T",
    "DEFAULT_ANIMATED_REFERENCE_FRAME_T",
    "PHYSICS_DATA_T",
    "PHYSICS_SYSTEM_T",
    "SKELETON_T",
    "BONE_T",
    "RAGDOLL_INSTANCE_T",
    "SKELETON_MAPPER_T",
]

from soulstruct_havok.types import hk550, hk2010, hk2014, hk2015, hk2016, hk2018


# region Basic
QS_TRANSFORM = tp.TypeVar(
    "QS_TRANSFORM",
    hk550.hkQsTransform,
    hk2010.hkQsTransform,
    hk2014.hkQsTransform,
    hk2015.hkQsTransform,
    hk2016.hkQsTransform,
    hk2018.hkQsTransform,
)
# endregion


# region Animations
ANIMATION_CONTAINER_T = tp.TypeVar(
    "ANIMATION_CONTAINER_T",
    hk550.hkaAnimationContainer,
    hk2010.hkaAnimationContainer,
    hk2014.hkaAnimationContainer,
    hk2015.hkaAnimationContainer,
    hk2016.hkaAnimationContainer,
    hk2018.hkaAnimationContainer,
)
ANIMATION_T = tp.TypeVar(
    "ANIMATION_T",
    hk550.hkaSkeletalAnimation,  # note old name
    hk2010.hkaAnimation,
    hk2014.hkaAnimation,
    hk2015.hkaAnimation,
    hk2016.hkaAnimation,
    hk2018.hkaAnimation,
)
ANIMATION_BINDING_T = tp.TypeVar(
    "ANIMATION_BINDING_T",
    hk550.hkaAnimationBinding,
    hk2010.hkaAnimationBinding,
    hk2014.hkaAnimationBinding,
    hk2015.hkaAnimationBinding,
    hk2016.hkaAnimationBinding,
    hk2018.hkaAnimationBinding,
)
INTERLEAVED_ANIMATION_T = tp.TypeVar(
    "INTERLEAVED_ANIMATION_T",
    hk550.hkaInterleavedSkeletalAnimation,  # note old name
    hk2010.hkaInterleavedUncompressedAnimation,
    hk2015.hkaInterleavedUncompressedAnimation,
    hk2016.hkaInterleavedUncompressedAnimation,
    hk2018.hkaInterleavedUncompressedAnimation,
)
SPLINE_ANIMATION_T = tp.TypeVar(
    "SPLINE_ANIMATION_T",
    hk550.hkaSplineSkeletalAnimation,  # note old name
    hk2010.hkaSplineCompressedAnimation,
    hk2015.hkaSplineCompressedAnimation,
    hk2016.hkaSplineCompressedAnimation,
    hk2018.hkaSplineCompressedAnimation,
)
DEFAULT_ANIMATED_REFERENCE_FRAME_T = tp.TypeVar(
    "DEFAULT_ANIMATED_REFERENCE_FRAME_T",
    hk550.hkaDefaultAnimatedReferenceFrame,
    hk2010.hkaDefaultAnimatedReferenceFrame,
    hk2015.hkaDefaultAnimatedReferenceFrame,
    hk2016.hkaDefaultAnimatedReferenceFrame,
    hk2018.hkaDefaultAnimatedReferenceFrame,
)
# endregion


# region Physics
PHYSICS_DATA_T = tp.TypeVar(
    "PHYSICS_DATA_T",
    hk550.hkpPhysicsData,
    hk2010.hkpPhysicsData,
    hk2015.hkpPhysicsData,
    hk2016.hkpPhysicsData,
)
PHYSICS_SYSTEM_T = tp.TypeVar(
    "PHYSICS_SYSTEM_T",
    hk550.hkpPhysicsSystem,
    hk2010.hkpPhysicsSystem,
    hk2015.hkpPhysicsSystem,
    hk2016.hkpPhysicsSystem,
)
# endregion


# region Skeletons
SKELETON_T = tp.TypeVar(
    "SKELETON_T",
    hk550.hkaSkeleton,
    hk2010.hkaSkeleton,
    hk2014.hkaSkeleton,
    hk2015.hkaSkeleton,
    hk2016.hkaSkeleton,
    hk2018.hkaSkeleton,
)
BONE_T = tp.TypeVar(
    "BONE_T",
    hk550.hkaBone,
    hk2010.hkaBone,
    hk2014.hkaBone,
    hk2015.hkaBone,
    hk2016.hkaBone,
    hk2018.hkaBone,
)
# endregion


# region Ragdolls
RAGDOLL_INSTANCE_T = tp.TypeVar(
    "RAGDOLL_INSTANCE_T",
    hk550.hkaRagdollInstance,
    hk2010.hkaRagdollInstance,
    hk2015.hkaRagdollInstance,
    hk2016.hkaRagdollInstance,
)
SKELETON_MAPPER_T = tp.TypeVar(
    "SKELETON_MAPPER_T",
    hk550.hkaSkeletonMapper,
    hk2010.hkaSkeletonMapper,
    hk2014.hkaSkeletonMapper,
    hk2015.hkaSkeletonMapper,
    hk2016.hkaSkeletonMapper,
    hk2018.hkaSkeletonMapper,
)
# endregion
