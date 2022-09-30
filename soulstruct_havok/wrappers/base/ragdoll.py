import typing as tp

from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2018

from .core import BaseWrapperHKX
from .utilities import scale_shape, scale_motion_state


SKELETON_TYPING = tp.Union[
    hk2010.hkaSkeleton, hk2014.hkaSkeleton, hk2015.hkaSkeleton, hk2018.hkaSkeleton,
]
PHYSICS_SYSTEM_TYPING = tp.Union[
    hk2010.hkpPhysicsSystem, hk2015.hkpPhysicsSystem
]
RAGDOLL_INSTANCE_TYPING = tp.Union[
    hk2010.hkaRagdollInstance, hk2015.hkaRagdollInstance,
]
SKELETON_MAPPER_TYPING = tp.Union[
    hk2010.hkaSkeletonMapper, hk2014.hkaSkeletonMapper, hk2015.hkaSkeletonMapper, hk2018.hkaSkeletonMapper
]


class RagdollHKX(BaseWrapperHKX):
    """Loads HKX objects that are found in a "Ragdoll" HKX file (inside `chrbnd` binder, e.g. `c0000.hkx`)."""

    standard_skeleton: SKELETON_TYPING
    ragdoll_skeleton: SKELETON_TYPING
    physics_system: PHYSICS_SYSTEM_TYPING
    ragdoll_instance: RAGDOLL_INSTANCE_TYPING
    ragdoll_to_standard_skeleton_mapper: SKELETON_MAPPER_TYPING
    standard_to_ragdoll_skeleton_mapper: SKELETON_MAPPER_TYPING

    def create_attributes(self):
        animation_container = self.get_variant_index(0, "hkaAnimationContainer")
        self.standard_skeleton = animation_container.skeletons[0]
        self.ragdoll_skeleton = animation_container.skeletons[1]
        physics_data = self.get_variant_index(1, "hkpPhysicsData")
        self.physics_system = physics_data.systems[0]
        self.ragdoll_instance = self.get_variant_index(2, "hkaRagdollInstance")
        # TODO: Is this the correct order?
        self.ragdoll_to_standard_skeleton_mapper = self.get_variant_index(3, "hkaSkeletonMapper")
        self.standard_to_ragdoll_skeleton_mapper = self.get_variant_index(4, "hkaSkeletonMapper")

    def scale(self, factor: float):
        """Scale all translation information, including:
            - bones in both the standard and ragdoll skeletons
            - rigid body collidables
            - motion state transforms and swept transforms
            - skeleton mapper transforms in both directions

        This is currently working well, though since actual "ragdoll mode" only occurs when certain enemies die, any
        mismatched (and probably harmless) physics will be more of an aesthetic issue.
        """
        for pose in self.standard_skeleton.referencePose:
            pose.translation *= factor
        for pose in self.ragdoll_skeleton.referencePose:
            pose.translation *= factor

        for rigid_body in self.physics_system.rigidBodies:
            scale_shape(rigid_body.collidable.shape, factor)

            # TODO: Experimental. Possibly index 3 should not be scaled. (Maybe always zero for ragdolls anyway.)
            rigid_body.motion.inertiaAndMassInv *= factor

            scale_motion_state(rigid_body.motion.motionState, factor)

        # TODO: constraint instance transforms?

        for mapper in (self.ragdoll_to_standard_skeleton_mapper, self.standard_to_ragdoll_skeleton_mapper):
            for simple in mapper.mapping.simpleMappings:
                simple.aFromBTransform.translation *= factor
            for chain in mapper.mapping.chainMappings:
                chain.startAFromBTransform.translation *= factor
