from __future__ import annotations

__all__ = ["PhysicsData", "ClothPhysicsData"]

from soulstruct.utilities.maths import Vector3, Vector4

from soulstruct_havok.enums import HavokModule
from soulstruct_havok.types.hk2014 import hknpPhysicsSceneData, hknpPhysicsSystemData
from soulstruct_havok.fromsoft.base.utilities import scale_hknp_shape, scale_constraint_data


class PhysicsData:
    """Loads HKX objects that just have collision physics, such as those in OBJBND binders or map collisions.

    Havok 2014 (and onwards), which uses the new `hknp` classes, differs from the base `PhysicsData` template.
    """

    havok_module: HavokModule
    physics_scene_data: hknpPhysicsSceneData

    def __init__(self, havok_module: HavokModule, physics_scene_data: hknpPhysicsSceneData):
        self.havok_module = havok_module
        self.physics_scene_data = physics_scene_data

    @property
    def physics_system_data(self) -> hknpPhysicsSystemData:
        return self.physics_scene_data.systemDatas[0]

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        """Scale all translation information, including:
            - rigid body collidables
            - motion state transforms and swept transforms
        """
        if isinstance(scale_factor, Vector3):
            scale_factor = Vector4.from_vector3(scale_factor)

        for body_c_info in self.physics_system_data.bodyCinfos:
            # TODO: Does not support Mopp shapes, but could using Mopper.
            scale_hknp_shape(body_c_info.shape, scale_factor)

        for constraint_c_info in self.physics_system_data.constraintCinfos:
            # TODO: Why don't we scale constraints here? Why only for cloth physics below?
            pass

        for motion_c_info in self.physics_system_data.motionCinfos:
            # TODO: scale other fields?:
            #  inverseMass
            #  massFactor
            #  inverseInertiaLocal
            motion_c_info.centerOfMassWorld *= scale_factor


class ClothPhysicsData(PhysicsData):
    """Physics with contraints found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`)."""

    def scale_all_translations(self, scale_factor: float | Vector3 | Vector4):
        """Scales constraint data in addition to rigid bodies.

        TODO: Since cloth is always in "ragdoll" mode, forces may need to be updated more cautiously here.
        """
        super().scale_all_translations(scale_factor)
        for constraint_c_info in self.physics_system_data.constraintCinfos:
            scale_constraint_data(constraint_c_info.constraintData, scale_factor)
