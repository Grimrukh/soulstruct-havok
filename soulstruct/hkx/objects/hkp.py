from __future__ import annotations

__all__ = ["PhysicsData", "RigidBody", "ConstraintInstance"]

import typing as tp

from soulstruct.utilities.maths import Vector4, Matrix3, Matrix4
from .base import HKXObject, HalfFloat, QuarterFloat

if tp.TYPE_CHECKING:
    from ..nodes import HKXNode


class PhysicsData(HKXObject):
    """hkpPhysicsData"""

    systems: list[tp.Optional[PhysicsSystem]]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.world_c_info = node["worldCinfo"]  # hkpWorldCinfo
        self.systems = [n.get_py_object(PhysicsSystem) for n in node["systems"]]


class PhysicsSystem(HKXObject):
    """hkpPhysicsSystem"""

    rigid_bodies: list[tp.Optional[RigidBody]]
    constraints: list[tp.Optional[ConstraintInstance]]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.rigid_bodies = [n.get_py_object(RigidBody) for n in node["rigidBodies"]]
        self.constraints = [n.get_py_object(ConstraintInstance) for n in node["constraints"]]
        self.actions = node["actions"]  # array of pointers
        self.phantoms = node["phantoms"]  # array of pointers
        self.name = node["name"]  # "Default Physics System"
        self.user_data = node["userData"]
        self.active = node["active"]


class Entity(HKXObject):
    """hkpEntity"""

    collidable: tp.Optional[LinkedCollidable]
    multi_thread_check: tp.Optional[MultiThreadCheck]
    motion: tp.Optional[MaxSizeMotion]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        # `world` is Opaque.
        self.user_data = node["userData"]  # hkUlong
        self.collidable = node["collidable"].get_py_object(LinkedCollidable)
        self.multi_thread_check = node["multiThreadCheck"].get_py_object(MultiThreadCheck)
        self.name = ""
        self.material = node["material"].get_py_object(Material)
        self.properties = node["properties"].value  # TODO: list of `hkSimpleProperty` nodes (empty)
        # `limitContactImpulseUtilAndFlag` is a void pointer.
        self.damage_multiplier = node["damageMultiplier"]
        # `breakableBody` is Opaque.
        self.solver_data = node["solverData"]
        self.storage_index = node["storageIndex"]
        self.contact_point_callback_delay = node["contactPointCallbackDelay"]
        self.constraints_master = node["constraintsMaster"].get_py_object(EntitySmallArraySerializeOverrideType)
        self.constraints_slave = node["constraintsSlave"].value  # TODO: list of `hkViewPtr` nodes (empty)
        self.constraint_runtime = node["constraintRuntime"]
        # `simulationIsland` is Opaque.
        self.auto_remove_level = node["autoRemoveLevel"]
        self.num_shape_keys_in_contact_pointer_properties = node["numShapeKeysInContactPointProperties"]
        self.response_modifier_flags = node["responseModifierFlags"]
        self.uid = node["uid"]
        self.spu_collision_callback = node["spuCollisionCallback"].get_py_object(EntitySpuCollisionCallback)
        self.motion = node["motion"].get_py_object(MaxSizeMotion)
        self.contact_listeners = node["contactListeners"].get_py_object(EntitySmallArraySerializeOverrideType)
        self.actions = node["actions"].get_py_object(EntitySmallArraySerializeOverrideType)
        self.local_frame = node["localFrame"]  # hkLocalFrame
        self.extended_listeners = node["extendedListeners"]  # hkpEntityExtendedListeners


class RigidBody(Entity):
    """hkpRigidBody"""
    # No additional data.


class LinkedCollidable(HKXObject):
    """hkpLinkedCollidable"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.shape = Shape.auto_shape_type(node["shape"])
        self.shape_key = node["shapeKey"]  # unsigned int
        # `motion` is Opaque.
        self.parent = node["parent"]  # hkpCdBody
        self.owner_offset = node["ownerOffset"]
        self.force_collide_onto_ppu = node["forceCollideOntoPpu"]
        self.shape_size_on_spu = node["shapeSizeOnSpu"]
        self.broad_phase_handle = None
        self.bounding_volume_data = node["boundingVolumeData"].get_py_object(CollidableBoundingVolumeData)
        self.allowed_penetration_depth = 0.0
        # `collisionEntries is Opaque.


class hkcdShape(HKXObject):
    """hkcdShape"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.type = node["type"]
        self.dispatch_type = node["dispatchType"]  # hkEnum
        self.bits_per_key = node["bitsPerKey"]
        self.shape_info_codec_type = node["shapeInfoCodecType"]  # hkEnum


class ShapeBase(hkcdShape):
    """hkpShapeBase"""
    # No additional data.


class Shape(ShapeBase):
    """"hkpShape"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.user_data = node["userData"]  # hkUlong

    @staticmethod
    def auto_shape_type(node: HKXNode) -> tp.Union[None, ConvexShape, CapsuleShape]:
        """Examines member names (dict keys) to determine shape, rather than loading types."""
        members = set(node.value.keys())
        if members >= {"radius", "vertexA", "vertexB"}:
            return node.get_py_object(CapsuleShape)
        elif members >= {"radius"}:
            return node.get_py_object(ConvexShape)
        raise TypeError(f"Could not detect `Shape` subclass from node keys: {members}")


class SphereRepShape(Shape):
    """hkpSphereRepShape"""
    # No additional data.


class ConvexShape(SphereRepShape):
    """hkpConvexShape"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.radius = node["radius"]


class CapsuleShape(ConvexShape):
    """hkpCapsuleShape"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.vertex_A = Vector4(node["vertexA"])
        self.vertex_B = Vector4(node["vertexB"])


class TypedBroadPhaseHandle(HKXObject):
    """hkpTypedBroadPhaseHandle"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.id = node["id"]
        self.type = node["type"]
        self.owner_offset = node["ownerOffset"]
        self.object_quality_type = node["objectQualityType"]
        self.collision_filter_info = node["collisionFilterInfo"]  # bit field


class CollidableBoundingVolumeData(HKXObject):
    """hkpCollidableBoundingVolumeData"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.min = node["min"]
        self.expansion_min = node["expansionMin"]
        self.expansion_shift = node["expansionShift"]
        self.max = node["max"]
        self.expansion_max = node["expansionMax"]
        self.padding = node["padding"]
        self.num_child_shape_aabbs = node["numChildShapeAabbs"]
        self.capacity_child_shape_aabs = node["capacityChildShapeAabbs"]
        # `childShapeAabbs` is Opaque.
        # `childShapeKeys` is Opaque.


class MultiThreadCheck(HKXObject):
    """hkMultiThreadCheck"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.thread_id = node["threadId"]
        self.stack_trace_id = node["stackTraceId"]
        self.mark_count = node["markCount"]
        self.mark_bit_stack = node["markBitStack"]


class EntitySpuCollisionCallback(HKXObject):
    """hkpEntitySpuCollisionCallback"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        # `util` is Opaque.
        self.capacity = node["capacity"]
        self.event_filter = node["eventFilter"]
        self.user_filter = node["userFilter"]


class Material(HKXObject):
    """hkpMaterial"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.response_type = node["responseType"]
        self.rolling_friction_multiplier = HalfFloat(node["rollingFrictionMultiplier"]["value"])
        self.friction = node["friction"]
        self.restitution = node["restitution"]


class Motion(HKXObject):
    """hkpMotion"""

    motion_state: tp.Optional[MotionState]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.type = node["type"]
        self.deactivation_integrate_counter = node["deactivationIntegrateCounter"]
        self.deactivation_num_inactive_frames = node["deactivationNumInactiveFrames"]  # tuple
        self.motion_state = node["motionState"].get_py_object(MotionState)
        self.inertia_and_mass_inv = Vector4(node["inertiaAndMassInv"])
        self.linear_velocity = Vector4(node["linearVelocity"])
        self.angular_velocity = Vector4(node["angularVelocity"])
        self.deactivation_ref_position = (
            Vector4(node["deactivationRefPosition"][0]),
            Vector4(node["deactivationRefPosition"][1])
        )
        self.saved_motion = node["savedMotion"]  # hkpMotion
        self.saved_quality_type_index = node["savedQualityTypeIndex"]
        self.gravity_factor = HalfFloat(node["gravityFactor"]["value"])


class MaxSizeMotion(Motion):
    """hkpMaxSizeMotion"""
    # No additional data.


class MotionState(HKXObject):
    """hkMotionState"""

    transform: Matrix4
    swept_transform: tp.Optional[SweptTransform]
    delta_angle: Vector4

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.transform = Matrix4.from_flat_column_order(node["transform"])
        self.swept_transform = node["sweptTransform"].get_py_object(SweptTransform)
        self.delta_angle = Vector4(node["deltaAngle"])
        self.object_radius = node["objectRadius"]
        self.linear_damping = HalfFloat(node["linearDamping"]["value"])
        self.angular_damping = HalfFloat(node["angularDamping"]["value"])
        self.max_linear_velocity = QuarterFloat(node["maxLinearVelocity"]["value"])
        self.max_angular_velocity = QuarterFloat(node["maxAngularVelocity"]["value"])
        self.deactivation_class = node["deactivationClass"]


class SweptTransform(HKXObject):
    """Tuple of five Vector4s.

    This was actually a Havok class, `hkSweptTransform`, in 2010 (and maybe some time after). It's represented just like
    that old class here.
    """

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.center_of_mass_0 = Vector4(node[0])
        self.center_of_mass_1 = Vector4(node[1])
        self.rotation_0 = Vector4(node[2])
        self.rotation_1 = Vector4(node[3])
        self.center_of_mass_local = Vector4(node[4])


class ConstraintInstance(HKXObject):
    """hkpConstraintInstance"""

    data: tp.Union[None, RagdollConstraintData, BallAndSocketConstraintData]
    listeners: tp.Optional[ConstraintInstanceSmallArraySerializeOverrideType]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        # `owner` is Opaque.
        self.data = ConstraintData.auto_constant_data_type(node["data"])
        self.constraint_modifiers = node["constraintModifiers"]  # TODO: hkpModifierConstraintAtoms (None)
        self.entities = [n.get_py_object(RigidBody) for n in node["entities"]]
        self.priority = node["priority"]
        self.want_runtime = node["wantRuntime"]
        self.destruction_remap_info = node["destructionRemapInfo"]
        self.listeners = node["listeners"].get_py_object(ConstraintInstanceSmallArraySerializeOverrideType)
        self.name = node["name"]  # TODO: generally matches Ragdoll skeleton bone name but likely optional
        self.user_data = node["userData"]
        # `internal` is Opaque.
        self.uid = node["uid"]


class ConstraintData(HKXObject):
    """hkpConstraintData"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.user_data = node["userData"]

    @staticmethod
    def auto_constant_data_type(node: HKXNode) -> tp.Union[None, RagdollConstraintData, BallAndSocketConstraintData]:
        if node.value is None:
            return None
        print(node.value)
        if "transforms" in node.value["atoms"].value:
            return node.get_py_object(RagdollConstraintData)
        elif "pivots" in node.value["atoms"].value:
            return node.get_py_object(BallAndSocketConstraintData)
        raise TypeError(f"Could not detect `ConstraintData` subtype from node.")


class RagdollConstraintData(ConstraintData):
    """hkpRagdollConstraintData"""

    atoms: tp.Optional[RagdollConstraintDataAtoms]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        if "2dAng" in node["atoms"].value:
            self.atoms = node["atoms"].get_py_object(HingeConstraintDataAtoms)
        else:
            self.atoms = node["atoms"].get_py_object(RagdollConstraintDataAtoms)


class HingeConstraintDataAtoms(HKXObject):
    """hkpHingeConstraintDataAtoms"""
    # TODO: This isn't in 2015 type database yet!

    transforms: tp.Optional[SetLocalTransformsConstraintAtom]
    setup_stabilization: tp.Optional[SetupStabilizationAtom]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.transforms = node["transforms"].get_py_object(SetLocalTransformsConstraintAtom)
        self.setup_stabilization = node["setupStabilization"].get_py_object(SetupStabilizationAtom)
        self.ang_2d = node["2dAng"]  # TODO: hkp2dAngConstraintAtom
        self.ball_socket = node["ballSocket"].get_py_object(BallSocketConstraintAtom)


class RagdollConstraintDataAtoms(HKXObject):
    """hkpRagdollConstraintDataAtoms"""

    transforms: tp.Optional[SetLocalTransformsConstraintAtom]
    setup_stabilization: tp.Optional[SetupStabilizationAtom]
    ragdoll_motors: tp.Optional[RagdollMotorConstraintAtom]
    ang_friction: tp.Optional[AngFrictionConstraintAtom]
    twist_limit: tp.Optional[TwistLimitConstraintAtom]
    cone_limit: tp.Optional[ConeLimitConstraintAtom]
    planes_limit: tp.Optional[ConeLimitConstraintAtom]
    ball_socket: tp.Optional[BallSocketConstraintAtom]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.transforms = node["transforms"].get_py_object(SetLocalTransformsConstraintAtom)
        self.setup_stabilization = node["setupStabilization"].get_py_object(SetupStabilizationAtom)
        self.ragdoll_motors = node["ragdollMotors"].get_py_object(RagdollMotorConstraintAtom)
        self.ang_friction = node["angFriction"].get_py_object(AngFrictionConstraintAtom)
        self.twist_limit = node["twistLimit"].get_py_object(TwistLimitConstraintAtom)
        self.cone_limit = node["coneLimit"].get_py_object(ConeLimitConstraintAtom)
        self.planes_limit = node["planesLimit"].get_py_object(ConeLimitConstraintAtom)
        self.ball_socket = node["ballSocket"].get_py_object(BallSocketConstraintAtom)


class ConstraintAtom(HKXObject):
    """hkpConstraintAtom"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.type = node["type"]


class SetLocalTransformsConstraintAtom(ConstraintAtom):
    """hkpSetLocalTransformsConstraintAtom"""

    transform_a: Matrix4
    transform_b: Matrix4

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.transform_a = Matrix4.from_flat_column_order(node["transformA"])
        self.transform_b = Matrix4.from_flat_column_order(node["transformB"])


class SetupStabilizationAtom(ConstraintAtom):
    """hkpSetupStabilizationAtom"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.enabled = node["enabled"]
        self.max_linear_impulse = node["maxLinImpulse"]
        self.max_angular_impulse = node["maxAngImpulse"]
        self.max_angle = node["maxAngle"]


class RagdollMotorConstraintAtom(ConstraintAtom):
    """hkpRagdollMotorConstraintAtom"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.is_enabled = node["isEnabled"]
        self.initialized_offset = node["initializedOffset"]
        self.previous_target_angles_offset = node["previousTargetAnglesOffset"]
        self.target_brca = node["target_bRca"]  # TODO: `hkMatrix3` is 12 values (first three columns?)
        self.motors = tuple(motor for motor in node["motors"].value)  # TODO: three `hkpConstraintMotor` pointers


class AngFrictionConstraintAtom(ConstraintAtom):
    """hkpAngFrictionConstraintAtom"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.is_enabled = node["isEnabled"]
        self.first_friction_axis = node["firstFrictionAxis"]
        self.num_friction_axis = node["numFrictionAxes"]
        self.max_friction_torque = node["maxFrictionTorque"]


class TwistLimitConstraintAtom(ConstraintAtom):
    """hkpTwistLimitConstraintAtom"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.is_enabled = node["isEnabled"]
        self.twist_axis = node["twistAxis"]
        self.ref_axis = node["refAxis"]
        self.min_angle = node["minAngle"]
        self.max_angle = node["maxAngle"]
        self.angular_limits_tau_factor = node["angularLimitsTauFactor"]
        self.angular_limits_damp_factor = node["angularLimitsDampFactor"]


class ConeLimitConstraintAtom(ConstraintAtom):
    """hkpConeLimitConstraintAtom"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.is_enabled = node["isEnabled"]
        self.twist_axis_in_A = node["twistAxisInA"]
        self.ref_axis_in_B = node["refAxisInB"]
        self.angle_measurement_mode = node["angleMeasurementMode"]
        self.mem_offset_to_angle_offset = node["memOffsetToAngleOffset"]
        self.min_angle = node["minAngle"]
        self.max_angle = node["maxAngle"]
        self.angular_limits_tau_factor = node["angularLimitsTauFactor"]
        self.angular_limits_damp_factor = node["angularLimitsDampFactor"]


class BallSocketConstraintAtom(ConstraintAtom):
    """hkpBallSocketConstraintAtom"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.solving_method = node["solvingMethod"]
        self.bodies_to_notify = node["bodiesToNotify"]
        self.velocity_stabilization_factor = QuarterFloat(node["velocityStabilizationFactor"]["value"])
        self.enable_linear_impulse_limit = node["enableLinearImpulseLimit"]
        self.breach_impulse = node["breachImpulse"]
        self.inertia_stabilization_factor = node["inertiaStabilizationFactor"]


class BallAndSocketConstraintData(ConstraintData):
    """hkpBallAndSocketConstraintData"""

    atoms: tp.Optional[BallAndSocketConstraintDataAtoms]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.atoms = node["atoms"].get_py_object(BallAndSocketConstraintDataAtoms)


class BallAndSocketConstraintDataAtoms(HKXObject):
    """hkpBallAndSocketConstraintDataAtoms"""

    pivots: tp.Optional[SetLocalTranslationsConstraintAtom]
    setup_stabilization: tp.Optional[SetupStabilizationAtom]
    ball_socket: tp.Optional[BallSocketConstraintAtom]

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.pivots = node["pivots"].get_py_object(SetLocalTranslationsConstraintAtom)
        self.setup_stabilization = node["setupStabilization"].get_py_object(SetupStabilizationAtom)
        self.ball_socket = node["ballSocket"].get_py_object(BallSocketConstraintAtom)


class SetLocalTranslationsConstraintAtom(ConstraintAtom):
    """hkpSetLocalTranslationsConstraintAtom"""

    translation_a: Vector4
    translation_b: Vector4

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.translation_a = Vector4(node["translationA"])
        self.translation_b = Vector4(node["translationB"])


class EntitySmallArraySerializeOverrideType(HKXObject):
    """hkpEntity::SmallArraySerializeOverrideType"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.data = node["data"]  # void pointer
        self.size = node["size"]
        self.capacity_and_flags = node["capacityAndFlags"]


class ConstraintInstanceSmallArraySerializeOverrideType(HKXObject):
    """hkpConstraint::InstanceSmallArraySerializeOverrideType"""

    def __init__(self, node: HKXNode):
        super().__init__(node)
        self.data = node["data"]  # void pointer
        self.size = node["size"]
        self.capacity_and_flags = node["capacityAndFlags"]
