from __future__ import annotations

import copy
import typing as tp
from pathlib import Path

from soulstruct import DSR_PATH, BB_PATH
from soulstruct.containers import Binder, BinderEntry
from soulstruct_havok.utilities.maths import TRSTransform, Vector3, Vector4, Quaternion

from soulstruct_havok.core import HKX, HavokFileFormat
from soulstruct_havok.types import hk2014, hk2015


# TODO: Now to convert 2014 ragdoll to 2015 (e.g. BB to DSR).
#  - Swap types. Iterate over HKX:
#    - When a 2014 `hk` instance is encountered, find the type with the same name in 2015.
#    - Load it by simply iterating over the 2015 members and retrieving the 2014 members with that name.
#    - If a 2014 member is no longer needed, it won't be used.
#    - If the 2015 type needs a new member, just raise an error for now; it will need to be taken care of manually.
#    - Iterate into members, which may still be 2015 types.
#    - Throughout all this, maintain a dictionary mapping the `id`s of 2014 instances to their 2015 instances.
#    - If an encountered instance's ID is already in that dict, use the same value.


class Converter_2014_2015:

    def __init__(self, hkx2014: HKX):
        self.converted_ids = {}  # type: dict[int, hk2015.hk]
        # TODO: Ideally, this would create a copy of HKX, but because it stores a type module as an attribute, default
        #  deepcopy() does not work.
        self.hkx = hkx2014
        self.hkx.root = self.convert(hkx2014.root)

    def convert(self, instance_2014: hk2014.hk) -> hk2015.hk:

        # TODO: Won't work; `hk` is currently the same. Need to check `__module__` or something instead.
        if isinstance(instance_2014, hk2015.hk):
            # Already converted (e.g. by the `hknp` pre-converter).
            return instance_2014

        if id(instance_2014) in self.converted_ids:
            return self.converted_ids[id(instance_2014)]

        try:
            convert_method = getattr(self, f"convert_{instance_2014.get_type_name()}")
        except AttributeError:
            return self.convert_default(instance_2014)
        else:
            # TODO: If the instance type is changed, the name/className of its `NamedVariant` may also need to change.
            #  Could scan variants at the end to fix this.
            return convert_method(instance_2014)

    def convert_default(self, instance_2014: hk2014.hk) -> hk2015.hk:
        try:
            hk_type_2015 = getattr(hk2015, instance_2014.get_type_name())  # type: tp.Type[hk2015.hk]
        except AttributeError:
            raise TypeError(f"Cannot find type `{type(instance_2014).__name__}` in `types.hk2015` module.")
        instance_2015 = self.converted_ids[id(instance_2014)] = hk_type_2015()  # type: hk2015.hk
        print(f"New instance: {type(instance_2015).__name__}")

        for parent_type in instance_2015.get_type_hierarchy():
            try:
                set_members_method = getattr(self, f"set_members_{parent_type.get_type_name()}")
            except AttributeError:
                self.set_members_default(instance_2014, instance_2015, parent_type)
            else:
                set_members_method(instance_2014, instance_2015)  # parent type implicit in method

        return instance_2015

    def set_members_default(self, instance_2014: hk2014.hk, instance_2015: hk2015.hk, parent_type: tp.Type[hk2015.hk]):
        """Copy member values for all local members in `parent_type`. (Will be called for each of the new instance's
        parent types.)"""
        for member in parent_type.local_members:
            try:
                member_value_2014 = getattr(instance_2014, member.py_name)
            except AttributeError:
                raise AttributeError(
                    f"`hk2014.{instance_2014.get_type_name()}` has no member '{member.py_name}'.\n"
                    f"    Members: {instance_2014.get_member_names()}"
                )
            else:
                if isinstance(member_value_2014, hk2014.hk):
                    member_value_2015 = self.convert(member_value_2014)
                elif (
                    isinstance(member_value_2014, list)
                    and member_value_2014 and isinstance(member_value_2014[0], hk2014.hk)
                ):
                    member_value_2015 = [self.convert(v) for v in member_value_2014]
                elif (
                    isinstance(member_value_2014, tuple)
                    and member_value_2014 and isinstance(member_value_2014[0], hk2014.hk)
                ):
                    member_value_2015 = tuple(self.convert(v) for v in member_value_2014)
                else:
                    member_value_2015 = member_value_2014  # Python primitive
                setattr(instance_2015, member.py_name, member_value_2015)

    def set_members_hkReferencedObject(
        self, instance_2014: hk2014.hkReferencedObject, instance_2015: hk2015.hkReferencedObject
    ):
        """`memSizeAndRefCount` is split into two members, `memSizeAndFlags` and `refCount`, in 2015."""
        assert_member_value(instance_2014, "memSizeAndRefCount", 0)
        instance_2015.memSizeAndFlags = 0
        instance_2015.refCount = 0


def assert_member_value(instance: hk2014.hk, member_name: str, value: tp.Any):
    if getattr(instance, member_name) != value:
        raise ValueError(
            f"Can only convert `hk2014.{instance.get_type_name()}.{member_name}` when its value is {repr(value)}."
        )


MISSING_MEMBER_DEFAULTS = {
    ("hkReferencedObject", "memSizeAndFlags"): 0,
    ("hkReferencedObject", "refCount"): 0,
    ("hkpTwistLimitConstraintAtom", "angularLimitsDampFactor"): 1.0,
    ("hkpConeLimitConstraintAtom", "angularLimitsDampFactor"): 1.0,
}


def convert_simple(instance: hk2014.hk, converted_ids: dict[int, hk2015.hk] = None):
    """Just iterates over members and updates types.

    Does not expect or handle any structural change EXCEPT for `memSizeAndFlags`/`refCount`.
    """
    if converted_ids is None:
        converted_ids = {}
    elif id(instance) in converted_ids:
        return converted_ids[id(instance)]

    try:
        hk_type_2015 = getattr(hk2015, instance.get_type_name())  # type: tp.Type[hk2015.hk]
    except AttributeError:
        raise TypeError(f"Cannot find type `{type(instance).__name__}` in `types.hk2015` module.")
    instance_2015 = converted_ids[id(instance)] = hk_type_2015()  # type: hk2015.hk

    for member in hk_type_2015.members:

        try:
            member_value_2014 = getattr(instance, member.py_name)
        except AttributeError:
            type_defining_member_name = hk_type_2015.get_type_with_member(member.name).get_type_name()
            try:
                member_value_2015 = MISSING_MEMBER_DEFAULTS[type_defining_member_name, member.name]
            except KeyError:
                raise AttributeError(
                    f"`hk2014.{instance.get_type_name()}` has no member '{member.name}' and no new default was given.\n"
                    f"    Members: {instance.get_member_names()}"
                )
        else:
            if isinstance(member_value_2014, hk2014.hk):
                member_value_2015 = convert_simple(member_value_2014, converted_ids)
            elif (
                isinstance(member_value_2014, list)
                and member_value_2014 and isinstance(member_value_2014[0], hk2014.hk)
            ):
                member_value_2015 = [convert_simple(v, converted_ids) for v in member_value_2014]
            elif (
                isinstance(member_value_2014, tuple)
                and member_value_2014 and isinstance(member_value_2014[0], hk2014.hk)
            ):
                member_value_2015 = tuple(convert_simple(v, converted_ids) for v in member_value_2014)
            else:
                member_value_2015 = member_value_2014  # Python primitive

        setattr(instance_2015, member.py_name, member_value_2015)

    return instance_2015


def convert_hknp_ragdoll_hkx_to_hkp(
    hkx: HKX,
):
    """Does initial work converting `hknp` types to `hkp` types for a ragdoll. Remaining work will be done by the
    standard instance-for-instance type converter.

    `hknp` uses the same large structure in its physics variant and ragdoll variant (single instance). `hkp`, however,
    does not have a ragdoll-specific physics data class, and so `hkaRagdollInstance` re-uses the rigid body instances
    defined in `hkpPhysicsData` (and for some reason, redefines `hkpConstraintInstance`s in a different order) and
    specifies the 'boneToRigidBodyMap' and 'skeleton'.

    This function takes the singular `hknpRagdollData` instance and returns the `hkpPhysicsData` instance (for the
    physics variant) and `hkaRagdollInstance` instance (for the ragdoll variant).
    """
    converted_ids = {}  # shared across all `convert_simple()` calls

    # noinspection PyTypeChecker
    root = copy.deepcopy(hkx.root)  # type: hk2014.hkRootLevelContainer

    # ANIMATION CONTAINER VARIANT

    animation_container: hk2015.hkaAnimationContainer
    # noinspection PyTypeChecker
    animation_container = convert_simple(root.namedVariants[0].variant, converted_ids)
    root.namedVariants[0] = hk2015.hkRootLevelContainerNamedVariant(
        name=root.namedVariants[0].name,
        className=root.namedVariants[0].className,
        variant=animation_container,
    )

    # PHYSICS DATA VARIANT

    # noinspection PyTypeChecker,PyUnresolvedReferences
    hknp_ragdoll_data = root.namedVariants[1].variant.systemDatas[0]  # type: hk2014.hknpRagdollData
    if root.namedVariants[2].variant is not hknp_ragdoll_data:
        raise ValueError(
            "Expected `hknpPhysicsSceneData.systemDatas[0]` to be the same `hknpRagdollData` as the ragdoll variant."
        )

    physics_data = hk2015.hkpPhysicsData(
        memSizeAndFlags=0,
        refCount=0,
        worldCinfo=None,
        systems=[],
    )

    root.namedVariants[1] = hk2015.hkRootLevelContainerNamedVariant(
        name="Physics Data",
        className="hkpPhysicsData",
        variant=physics_data,
    )

    hkp_physics_system = hk2015.hkpPhysicsSystem(
        memSizeAndFlags=0,
        refCount=0,
        rigidBodies=[],  # constructed below
        constraints=[],  # constructed below
        actions=[],
        phantoms=[],
        name="Default Physics System",
        userData=0,
        active=True,
    )
    physics_data.systems = [hkp_physics_system]

    for i in range(len(hknp_ragdoll_data.bodyCinfos)):

        hknp_body_c_info = hknp_ragdoll_data.bodyCinfos[i]
        hknp_material = hknp_ragdoll_data.materials[hknp_body_c_info.materialId]  # not actually used
        hknp_motion_c_info = hknp_ragdoll_data.motionCinfos[hknp_body_c_info.motionId]
        hknp_motion_properties = hknp_ragdoll_data.motionProperties[hknp_motion_c_info.motionPropertiesId]  # not used

        hknp_quat_transform = TRSTransform(
            Vector3(hknp_body_c_info.position[:3]),
            Quaternion(hknp_body_c_info.orientation),
            Vector3.one(),  # normal scale
        )

        hkp_physics_system.rigidBodies.append(
            hk2015.hkpRigidBody(
                memSizeAndFlags=0,
                refCount=0,
                world=None,
                userData=hknp_body_c_info.userData,
                collidable=hk2015.hkpLinkedCollidable(
                    shape=convert_hknp_shape_to_hkp(hknp_body_c_info.shape),
                    shapeKey=4294967295,
                    motion=None,
                    parent=None,
                    ownerOffset=0,
                    forceCollideOntoPpu=0,
                    shapeSizeOnSpu=0,
                    broadPhaseHandle=hk2015.hkpTypedBroadPhaseHandle(
                        id=0,
                        type=1,
                        ownerOffset=0,
                        objectQualityType=4,
                        collisionFilterInfo=hknp_body_c_info.collisionFilterInfo,
                    ),
                    boundingVolumeData=hk2015.hkpCollidableBoundingVolumeData(
                        min=(0, 0, 0),
                        expansionMin=(0, 0, 0),
                        expansionShift=0,
                        max=(0, 0, 0),
                        expansionMax=(0, 0, 0),
                        padding=0,
                        numChildShapeAabbs=0,
                        capacityChildShapeAabbs=0,
                        childShapeAabbs=None,
                        childShapeKeys=None,
                    ),
                    allowedPenetrationDepth=0.05,  # TODO: Not specified in hknp. This is a rough value.
                    collisionEntries=[],
                ),
                multiThreadCheck=hk2015.hkMultiThreadCheck(threadId=0, stackTraceId=0, markCount=0, markBitStack=0),
                name=hknp_body_c_info.name,
                properties=[],
                material=hk2015.hkpMaterial(  # TODO: constant for all Capra Demon rigid bodies
                    responseType=1,
                    rollingFrictionMultiplier=hk2015.hkHalf16(value=0),
                    friction=0.30000001192092896,  # TODO: stored as `hkHalf16` in hknp rather than float
                    restitution=0.800000011920929,  # TODO: stored as `hkHalf16` in hknp rather than float
                ),
                limitContactImpulseUtilAndFlag=None,
                damageMultiplier=1.0,
                breakableBody=None,
                solverData=0,
                storageIndex=65535,
                contactPointCallbackDelay=65535,
                constraintsMaster=hk2015.hkpEntitySmallArraySerializeOverrideType(
                    data=None, size=0, capacityAndFlags=0
                ),
                constraintsSlave=[],
                constraintRuntime=[],
                simulationIsland=None,
                autoRemoveLevel=0,
                numShapeKeysInContactPointProperties=0,
                responseModifierFlags=0,
                uid=4294967295,
                spuCollisionCallback=hk2015.hkpEntitySpuCollisionCallback(
                    util=None, capacity=0, eventFilter=3, userFilter=1
                ),
                motion=hk2015.hkpMaxSizeMotion(
                    memSizeAndFlags=0,
                    refCount=0,
                    type=3,  # TODO: mostly 3, sometimes 2 in Capra Demon. Can't find corresponding field in hknp.
                    deactivationIntegrateCounter=15,
                    deactivationNumInactiveFrames=(49152, 49152),
                    # TODO: Use my existing motion conversion.
                    motionState=hk2015.hkMotionState(
                        transform=tuple(hknp_quat_transform.to_matrix4().to_flat_column_order()),
                        sweptTransform=(
                            hknp_motion_c_info.centerOfMassWorld,
                            hknp_motion_c_info.centerOfMassWorld,
                            hknp_motion_c_info.orientation,  # quaternion
                            hknp_motion_c_info.orientation,  # quaternion
                            hknp_motion_c_info.centerOfMassWorld,  # TODO: actually differs subtly from first two rows
                        ),
                        deltaAngle=(0.0, 0.0, 0.0, 0.0),
                        objectRadius=hknp_body_c_info.shape.convexRadius * 3.0,  # TODO: very rough
                        linearDamping=hk2015.hkHalf16(value=0),
                        angularDamping=hk2015.hkHalf16(value=15692),
                        timeFactor=hk2015.hkHalf16(value=16256),
                        maxLinearVelocity=hk2015.hkUFloat8(value=127),
                        maxAngularVelocity=hk2015.hkUFloat8(value=127),
                        deactivationClass=2,
                    ),
                    # TODO: Best guess for correspondence here (seems right).
                    inertiaAndMassInv=hknp_motion_c_info.inverseInertiaLocal[:3] + (hknp_motion_c_info.inverseMass,),
                    linearVelocity=hknp_motion_c_info.linearVelocity,
                    angularVelocity=hknp_motion_c_info.angularVelocity,
                    deactivationRefPosition=(
                        (0.0, 0.0, 0.0, 0.0),
                        (0.0, 0.0, 0.0, 0.0),
                    ),
                    deactivationRefOrientation=(0, 0),
                    savedMotion=None,
                    savedQualityTypeIndex=199,
                    gravityFactor=hk2015.hkHalf16(value=16256),
                ),
                contactListeners=hk2015.hkpEntitySmallArraySerializeOverrideType(
                    data=None,
                    size=0,
                    capacityAndFlags=0,
                ),
                actions=hk2015.hkpEntitySmallArraySerializeOverrideType(
                    data=None,
                    size=0,
                    capacityAndFlags=0,
                ),
                localFrame=None,
                extendedListeners=None,
            )
        )

    # for i in range(len(hknp_ragdoll_data.constraintCinfos)):
    #
    #     hknp_constraint = hknp_ragdoll_data.constraintCinfos[i]
    #
    #     # noinspection PyTypeChecker
    #     hkp_physics_system.constraints.append(
    #         hk2015.hkpConstraintInstance(
    #             memSizeAndFlags=0,
    #             refCount=0,
    #             owner=None,
    #             data=convert_simple(hknp_constraint.constraintData),
    #             constraintModifiers=None,
    #             entities=(
    #                 hkp_physics_system.rigidBodies[hknp_constraint.bodyA],
    #                 hkp_physics_system.rigidBodies[hknp_constraint.bodyB],
    #             ),
    #             priority=1,
    #             wantRuntime=True,
    #             destructionRemapInfo=0,
    #             listeners=hk2015.hkpConstraintInstanceSmallArraySerializeOverrideType(
    #                 data=None,
    #                 size=0,
    #                 capacityAndFlags=0,
    #             ),
    #             name=hkp_physics_system.rigidBodies[hknp_constraint.bodyA].name,
    #             userData=0,
    #             internal=None,
    #             uid=0,
    #         )
    #     )

    # RAGDOLL VARIANT

    # Rigid bodies are reordered by bone order for `hkaRagdollInstance`.
    ordered_rigid_bodies = []
    ordered_constraints = []
    ragdoll_skeleton = animation_container.skeletons[1]
    for bone in ragdoll_skeleton.bones:  # exclude pelvis bone
        for i, rigid_body in enumerate(hkp_physics_system.rigidBodies):
            if rigid_body.name == bone.name:
                ordered_rigid_bodies.append(rigid_body)
                # if bone is not ragdoll_skeleton.bones[0]:  # root bone (Pelvis) has no constraint
                #     # TODO: Actual file duplicates the constraints from physics. Seems unnecessary.
                #     ordered_constraints.append(copy.deepcopy(hkp_physics_system.constraints[i - 1]))

    ragdoll_instance = hk2015.hkaRagdollInstance(
        memSizeAndFlags=0,
        refCount=0,
        rigidBodies=ordered_rigid_bodies,
        constraints=ordered_constraints,
        boneToRigidBodyMap=list(range(len(ordered_rigid_bodies) - 1)),
        skeleton=ragdoll_skeleton,
    )
    print(ragdoll_instance.boneToRigidBodyMap)

    root.namedVariants[2] = hk2015.hkRootLevelContainerNamedVariant(
        name="RagdollInstance",
        className="hkaRagdollInstance",
        variant=ragdoll_instance,
    )

    # SKELETON MAPPER VARIANTS

    # Skeleton mappers have no structural changes. (The `hkaSkeleton` instances have already been converted above and
    # will be found in `converted_ids`.)
    root.namedVariants[3] = hk2015.hkRootLevelContainerNamedVariant(
        name="SkeletonMapper",
        className="hkaSkeletonMapper",
        variant=convert_simple(root.namedVariants[3].variant, converted_ids),
    )
    root.namedVariants[4] = hk2015.hkRootLevelContainerNamedVariant(
        name="SkeletonMapper",
        className="hkaSkeletonMapper",
        variant=convert_simple(root.namedVariants[4].variant, converted_ids),
    )

    # TODO: Conversion works WITHOUT constraints.
    root.namedVariants[1].variant.systems[0].constraints = []
    root.namedVariants[2].variant.constraints = []

    hkx.root = hk2015.hkRootLevelContainer(namedVariants=root.namedVariants)


def convert_hknp_shape_to_hkp(hknp_shape: hk2014.hknpShape) -> hk2015.hkpShape:
    """Convert a `hknp` "new" shape to an old `hkp` shape.

    TODO: Can only handle `hknpConvexPolytopeShape` and `hknpCapsuleShape` input right now, and converts both to
     `hkpCapsuleShape`.
    """
    if isinstance(hknp_shape, hk2014.hknpConvexPolytopeShape):
        # Convert convex polytope shape to an approximating capsule.
        capsule_axis = 0
        w = 0.1
        vertices = sorted(hknp_shape.vertices, key=lambda x: x[capsule_axis])
        a_verts = vertices[:4]
        b_verts = vertices[4:]
        vertex_a = Vector4([sum(v[i] for v in a_verts) / 4 for i in range(3)] + [w])
        vertex_b = Vector4([sum(v[i] for v in b_verts) / 4 for i in range(3)] + [w])
        return hk2015.hkpCapsuleShape(
            memSizeAndFlags=0,
            refCount=0,
            type=0,
            dispatchType=0,  # TODO: given in `hknpShape`, but always zero here apparently anyway
            bitsPerKey=0,  # TODO: may correspond to 'numShapeKeyBits' in `hknpShape`
            shapeInfoCodecType=0,
            userData=0,  # TODO: ditto
            radius=hknp_shape.convexRadius,
            vertexA=vertex_a,
            vertexB=vertex_b,
        )
    elif isinstance(hknp_shape, hk2014.hknpCapsuleShape):
        return hk2015.hkpCapsuleShape(
            memSizeAndFlags=0,
            refCount=0,
            dispatchType=0,  # TODO: given in `hknpShape`, but always zero here apparently anyway
            bitsPerKey=0,  # TODO: may correspond to 'numShapeKeyBits' in `hknpShape`
            shapeInfoCodecType=0,
            userData=0,  # TODO: ditto
            radius=hknp_shape.convexRadius,
            vertexA=hknp_shape.a,
            vertexB=hknp_shape.b,
        )

    raise TypeError(f"Cannot convert `hknp` shape type: {hknp_shape.get_type_name()}")


def test_ragdoll_conversion():

    source_model = 2310
    dest_model = 5600

    bb_chrbnd = Binder.from_path(BB_PATH + f"/chr/c{source_model}.chrbnd.dcx")
    bb_hkx = HKX.from_binder_entry(bb_chrbnd[300])
    print("Opened BB HKX.")
    convert_hknp_ragdoll_hkx_to_hkp(bb_hkx)
    print("Conversion successful.")
    h = bb_hkx.get_root_tree_string()
    Path(f"c{source_model}_bb_2015.txt").write_text(h)
    bb_hkx.hk_format = HavokFileFormat.Tagfile

    game_chrbnd = Binder.from_path(DSR_PATH + f"/chr/c{dest_model}.chrbnd.dcx")
    game_chrbnd[300].set_from_binary_file(bb_hkx)
    game_chrbnd.write()
    print(f"Written to game CHRBND: {dest_model}")

    # from soulstruct import FLVER
    # bb_anibnd = Binder(BB_PATH + f"/chr/c{source_model}.anibnd.dcx")
    # skeleton = HKX(bb_anibnd[1000000])
    # print(len(skeleton.root.namedVariants[0].variant.skeletons[0].bones))
    # flver = FLVER(game_chrbnd[200])
    # print(len(bb_hkx.root.namedVariants[0].variant.skeletons[0].bones))
    # print(len(flver.bones))


# noinspection PyUnresolvedReferences
def examine_dsr_ragdolls():
    ice_king_ragdoll = HKX.from_path(
        r"C:\Steam\steamapps\common\DARK SOULS REMASTERED (Nightfall)\chr\c5600-chrbnd-dcx\c5600.hkx"
    )

    chr_dir = Path(DSR_PATH + "/chr")
    capra_chrbnd = Binder.from_path(chr_dir / "c2240.chrbnd.dcx")
    capra_ragdoll = HKX.from_binder_entry(capra_chrbnd[300])

    # capra_chrbnd[300].data = capra_ragdoll.pack()
    # capra_chrbnd.write()

    # noinspection PyTypeChecker,PyUnresolvedReferences
    def print_info(ragdoll: HKX):
        root = ragdoll.root  # type: hk2015.hkRootLevelContainer
        animation_container = root.namedVariants[0].variant  # type: hk2015.hkaAnimationContainer
        print("  Animation container:")
        print(f"    Skeleton 0 bones: {len(animation_container.skeletons[0].bones)}")
        print(f"    Skeleton 1 bones: {len(animation_container.skeletons[1].bones)}")
        physics_system = root.namedVariants[1].variant.systems[0]  # type: hk2015.hkpPhysicsSystem
        print("  Physics system:")
        print(f"    Rigid bodies: {len(physics_system.rigidBodies)}")
        mapper_0 = root.namedVariants[3].variant  # type: hk2015.hkaSkeletonMapper
        print("  Skeleton mapper 0:")
        print(f"    Simple mappings: {len(mapper_0.mapping.simpleMappings)}")
        print(f"    Chain mappings: {len(mapper_0.mapping.chainMappings)}")
        print(f"    Unmapped bones: {mapper_0.mapping.unmappedBones}")
        mapper_1 = root.namedVariants[4].variant  # type: hk2015.hkaSkeletonMapper
        print("  Skeleton mapper 1:")
        print(f"    Simple mappings: {len(mapper_1.mapping.simpleMappings)}")
        print(f"    Chain mappings: {len(mapper_1.mapping.chainMappings)}")
        print(f"    Unmapped bones: {mapper_1.mapping.unmappedBones}")

    # noinspection PyPep8Naming
    def inject_skeleton(source_skel: hk2015.hkaSkeleton, dest_skel: hk2015.hkaSkeleton):
        dest_skel.name = source_skel.name
        dest_skel.parentIndices = source_skel.parentIndices.copy()
        if len(dest_skel.bones) > len(source_skel.bones):
            dest_skel.bones = dest_skel.bones[:len(source_skel.bones)]
            dest_skel.referencePose = dest_skel.referencePose[:len(source_skel.referencePose)]
        else:
            while len(dest_skel.bones) < len(source_skel.bones):
                dest_skel.bones.append(hk2015.hkaBone())
                dest_skel.referencePose.append(hk2015.hkQsTransform())
        for i, bone in enumerate(source_skel.bones):
            dest_skel.bones[i].name = bone.name
            dest_skel.bones[i].lockTranslation = bone.lockTranslation
            pose = source_skel.referencePose[i]
            dest_skel.referencePose[i].translation = pose.translation
            dest_skel.referencePose[i].rotation = pose.rotation
            dest_skel.referencePose[i].scale = pose.scale
        for other in ("referenceFloats", "floatSlots", "localFrames", "partitions"):
            setattr(dest_skel, other, getattr(source_skel, other))

    # noinspection PyTypeChecker,PyUnresolvedReferences
    def inject_physics(source_physics: hk2015.hkpPhysicsSystem, dest_physics: hk2015.hkpPhysicsSystem):
        # Assumes all capsules.
        for i, rigidbody in enumerate(source_physics.rigidBodies):
            dest_rigidbody = dest_physics.rigidBodies[i]
            for capsule_attr in ("radius", "vertexA", "vertexB"):
                setattr(
                    dest_rigidbody.collidable.shape,
                    capsule_attr,
                    getattr(rigidbody.collidable.shape, capsule_attr),
                )
            dest_rigidbody.motion.motionState.transform = rigidbody.motion.motionState.transform
            dest_rigidbody.motion.motionState.sweptTransform = rigidbody.motion.motionState.sweptTransform
            dest_rigidbody.motion.motionState.objectRadius = rigidbody.motion.motionState.objectRadius
            dest_rigidbody.name = rigidbody.name
            # TODO: material
        dest_physics.constraints = []

    # noinspection PyPep8Naming
    def inject_skeleton_mapper(source_mapper: hk2015.hkaSkeletonMapper, dest_mapper: hk2015.hkaSkeletonMapper):
        # Skeletons already changed.
        mapping = source_mapper.mapping
        dest_mapping = dest_mapper.mapping

        if len(dest_mapping.simpleMappings) > len(mapping.simpleMappings):
            dest_mapping.simpleMappings = dest_mapping.simpleMappings[:len(mapping.simpleMappings)]
        else:
            while len(dest_mapping.simpleMappings) < len(mapping.simpleMappings):
                dest_mapping.simpleMappings.append(hk2015.hkaSkeletonMapperDataSimpleMapping(
                    aFromBTransform=hk2015.hkQsTransform.identity(),
                ))

        for i, simple_mapping in enumerate(mapping.simpleMappings):
            dest_mapping.simpleMappings[i].boneA = simple_mapping.boneA
            dest_mapping.simpleMappings[i].boneB = simple_mapping.boneB
            dest_mapping.simpleMappings[i].aFromBTransform.translation = simple_mapping.aFromBTransform.translation
            dest_mapping.simpleMappings[i].aFromBTransform.rotation = simple_mapping.aFromBTransform.rotation
            dest_mapping.simpleMappings[i].aFromBTransform.scale = simple_mapping.aFromBTransform.scale

        if len(dest_mapping.chainMappings) > len(mapping.chainMappings):
            dest_mapping.chainMappings = dest_mapping.chainMappings[:len(mapping.chainMappings)]
        else:
            while len(dest_mapping.chainMappings) < len(mapping.chainMappings):
                dest_mapping.chainMappings.append(hk2015.hkaSkeletonMapperDataChainMapping(
                    startAFromBTransform=hk2015.hkQsTransform.identity(),
                    endAFromBTransform=hk2015.hkQsTransform.identity(),
                ))

        for i, chain_mapping in enumerate(mapping.chainMappings):

            chain_start_transform = chain_mapping.startAFromBTransform
            chain_end_transform = chain_mapping.endAFromBTransform

            dest_mapping.chainMappings[i].startBoneA = chain_mapping.startBoneA
            dest_mapping.chainMappings[i].endBoneA = chain_mapping.endBoneA
            dest_mapping.chainMappings[i].startBoneB = chain_mapping.startBoneB
            dest_mapping.chainMappings[i].endBoneB = chain_mapping.endBoneB
            dest_mapping.chainMappings[i].startAFromBTransform.translation = chain_start_transform.translation
            dest_mapping.chainMappings[i].startAFromBTransform.rotation = chain_start_transform.rotation
            dest_mapping.chainMappings[i].startAFromBTransform.scale = chain_start_transform.scale
            dest_mapping.chainMappings[i].endAFromBTransform.translation = chain_end_transform.translation
            dest_mapping.chainMappings[i].endAFromBTransform.rotation = chain_end_transform.rotation
            dest_mapping.chainMappings[i].endAFromBTransform.scale = chain_end_transform.scale
        dest_mapping.unmappedBones = mapping.unmappedBones.copy()

    for skel_i in (0, 1):
        inject_skeleton(
            ice_king_ragdoll.root.namedVariants[0].variant.skeletons[skel_i],
            capra_ragdoll.root.namedVariants[0].variant.skeletons[skel_i],
        )

    inject_physics(
        ice_king_ragdoll.root.namedVariants[1].variant.systems[0],
        capra_ragdoll.root.namedVariants[1].variant.systems[0],
    )

    inject_skeleton_mapper(
        ice_king_ragdoll.root.namedVariants[3].variant,
        capra_ragdoll.root.namedVariants[3].variant,
    )
    inject_skeleton_mapper(
        ice_king_ragdoll.root.namedVariants[4].variant,
        capra_ragdoll.root.namedVariants[4].variant,
    )

    # `hkaRagdollInstance` points to same rigidbodies already edited above.
    capra_ragdoll.root.namedVariants[2].variant.constraints = []

    print("Ice King:")
    print_info(ice_king_ragdoll)
    print("Capra Demon:")
    print_info(capra_ragdoll)

    ice_king_chrbnd = Binder.from_path(chr_dir / "c5600.chrbnd.dcx")

    if 300 in ice_king_chrbnd.get_entry_ids():
        ice_king_chrbnd.remove_entry_id(300)
    ice_king_chrbnd.add_entry(BinderEntry(
        data=capra_ragdoll.pack(),
        entry_id=300,
        path="N:\\FRPG\\data\\INTERROOT_x64\\chr\\c5600\\c5600.hkx",
        flags=0x2,
    ))
    ice_king_chrbnd.write()
