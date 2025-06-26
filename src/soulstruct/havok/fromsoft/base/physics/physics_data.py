from __future__ import annotations

__all__ = ["PhysicsData"]

import typing as tp

from soulstruct.utilities.maths import Vector3, Vector4

from soulstruct.havok.enums import HavokModule
from soulstruct.havok.fromsoft.base.type_vars import PHYSICS_DATA_T, PHYSICS_SYSTEM_T
from soulstruct.havok.fromsoft.base.utilities import scale_shape, scale_motion_state


class PhysicsData(tp.Generic[PHYSICS_DATA_T, PHYSICS_SYSTEM_T]):
    """Loads HKX objects that just have collision physics, such as those in OBJBND binders or map collisions."""

    havok_module: HavokModule
    physics_data: PHYSICS_DATA_T

    def __init__(self, havok_module: HavokModule, physics_data: PHYSICS_DATA_T):
        self.havok_module = havok_module
        self.physics_data = physics_data

    @property
    def physics_system(self) -> PHYSICS_SYSTEM_T:
        return self.physics_data.systems[0]

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        """Scale all translation information, including:
            - rigid body collidables
            - motion state transforms and swept transforms
        """
        if isinstance(scale_factor, Vector3):
            scale_factor = Vector4.from_vector3(scale_factor)
        for rigid_body in self.physics_system.rigidBodies:
            # TODO: Does not support Mopp shapes, but could using Mopper.
            scale_shape(rigid_body.collidable.shape, scale_factor)

            # TODO: Experimental. Possibly index 3 should not be scaled. (Maybe always zero for ragdolls anyway.)
            rigid_body.motion.inertiaAndMassInv *= scale_factor

            scale_motion_state(rigid_body.motion.motionState, scale_factor)
