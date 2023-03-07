from __future__ import annotations

__all__ = ["PhysicsData", "ClothPhysicsData"]

import typing as tp
from types import ModuleType

from soulstruct.utilities.maths import Vector3, Vector4

from .type_vars import PHYSICS_DATA_T, PHYSICS_SYSTEM_T
from .utilities import scale_shape, scale_motion_state, scale_constraint_data


class PhysicsData(tp.Generic[PHYSICS_DATA_T, PHYSICS_SYSTEM_T]):
    """Loads HKX objects that just have collision physics, such as those in OBJBND binders or map collisions."""

    types_module: ModuleType
    physics_data: PHYSICS_DATA_T

    def __init__(self, types_module: ModuleType, physics_data: PHYSICS_DATA_T):
        self.types_module = types_module
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


class ClothPhysicsData(PhysicsData[PHYSICS_DATA_T, PHYSICS_SYSTEM_T]):
    """Physics with contraints found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`)."""

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        """Scales constraint data in addition to rigid bodies.

        TODO: Since cloth is always in "ragdoll" mode, forces may need to be updated more cautiously here.
        """
        super().scale_all_translations(scale_factor)
        for constraint_instance in self.physics_system.constraints:
            scale_constraint_data(constraint_instance.data, scale_factor)
