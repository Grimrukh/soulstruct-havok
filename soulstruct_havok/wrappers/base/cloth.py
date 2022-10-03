from __future__ import annotations

import abc
import typing as tp

from soulstruct_havok.types import hk2010, hk2015

from .core import BaseWrapperHKX
from .utilities import scale_shape, scale_motion_state, scale_constraint_data


PHYSICS_SYSTEM_TYPING = tp.Union[
    hk2010.hkpPhysicsSystem, hk2015.hkpPhysicsSystem
]


class BaseClothHKX(BaseWrapperHKX, abc.ABC):
    """Loads HKX objects that are found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`).

    This file is not used for every character - only those with cloth physics (e.g. capes).
    """

    physics_system: PHYSICS_SYSTEM_TYPING

    def create_attributes(self):
        physics_data = self.get_variant_index(0, "hkpPhysicsData")
        self.physics_system = physics_data.systems[0]

    def scale(self, factor: float):
        """Scale all translation information, including:
            - rigid body collidables
            - motion state transforms and swept transforms

        TODO: Since cloth is always in "ragdoll" mode, forces may need to be updated more cautiously here.
        """
        for rigid_body in self.physics_system.rigidBodies:
            scale_shape(rigid_body.collidable.shape, factor)

            # TODO: Experimental. Possibly index 3 should not be scaled. (Also, maybe scales as cube?)
            rigid_body.motion.inertiaAndMassInv *= factor

            scale_motion_state(rigid_body.motion.motionState, factor)

        for constraint_instance in self.physics_system.constraints:
            scale_constraint_data(constraint_instance.data, factor)
