from __future__ import annotations

import abc
import typing as tp

from soulstruct_havok.types import hk2010, hk2015

from .core import BaseWrapperHKX
from .utilities import scale_shape, scale_motion_state


PHYSICS_SYSTEM_TYPING = tp.Union[
    hk2010.hkpPhysicsSystem, hk2015.hkpPhysicsSystem
]


class BaseCollisionHKX(BaseWrapperHKX, abc.ABC):
    """Loads HKX objects that just have collision physics, such as those in OBJBND binders or map collisions."""

    physics_system: PHYSICS_SYSTEM_TYPING

    def create_attributes(self):
        physics_data = self.get_variant_index(0, "hkpPhysicsData")
        self.physics_system = physics_data.systems[0]

    def scale(self, factor: float):
        """Scale all translation information, including:
            - rigid body collidables
            - motion state transforms and swept transforms

        Note that this is a subset of `BaseRagdollHKX` scaling.
        """
        for rigid_body in self.physics_system.rigidBodies:
            # TODO: Does not support Mopp shapes, but could using Mopper.
            scale_shape(rigid_body.collidable.shape, factor)

            # TODO: Experimental. Possibly index 3 should not be scaled. (Maybe always zero for ragdolls anyway.)
            rigid_body.motion.inertiaAndMassInv *= factor

            scale_motion_state(rigid_body.motion.motionState, factor)
