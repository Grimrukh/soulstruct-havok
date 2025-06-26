from __future__ import annotations

__all__ = ["ClothPhysicsData"]

from soulstruct.utilities.maths import Vector3, Vector4

from ..core import BaseWrappedHKX
from ..type_vars import PHYSICS_DATA_T, PHYSICS_SYSTEM_T
from ..utilities import scale_constraint_data
from .physics_data import PhysicsData


class ClothPhysicsData(PhysicsData[PHYSICS_DATA_T, PHYSICS_SYSTEM_T]):
    """Physics with contraints found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`)."""

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        """Scales constraint data in addition to rigid bodies.

        TODO: Since cloth is always in "ragdoll" mode, forces may need to be updated more cautiously here.
        """
        super().scale_all_translations(scale_factor)
        for constraint_instance in self.physics_system.constraints:
            scale_constraint_data(constraint_instance.data, scale_factor)
