from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hknpMaterialLibrary import hknpMaterialLibrary
from .hknpMotionPropertiesLibrary import hknpMotionPropertiesLibrary
from .hknpBodyQualityLibrary import hknpBodyQualityLibrary
from .hknpWorldCinfoSimulationType import hknpWorldCinfoSimulationType
from .hknpWorldCinfoLeavingBroadPhaseBehavior import hknpWorldCinfoLeavingBroadPhaseBehavior
from .hkAabb import hkAabb
from .hknpBroadPhaseConfig import hknpBroadPhaseConfig
from .hknpCollisionFilter import hknpCollisionFilter
from .hknpShapeTagCodec import hknpShapeTagCodec


class hknpWorldCinfo(hk):
    alignment = 16
    byte_size = 256
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 5

    local_members = (
        Member(0, "bodyBufferCapacity", hkInt32),
        Member(8, "userBodyBuffer", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(16, "motionBufferCapacity", hkInt32),
        Member(24, "userMotionBuffer", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "constraintBufferCapacity", hkInt32),
        Member(40, "userConstraintBuffer", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(48, "persistentStreamAllocator", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(56, "materialLibrary", Ptr(hknpMaterialLibrary)),
        Member(64, "motionPropertiesLibrary", Ptr(hknpMotionPropertiesLibrary)),
        Member(72, "qualityLibrary", Ptr(hknpBodyQualityLibrary)),
        Member(80, "simulationType", hkEnum(hknpWorldCinfoSimulationType, hkUint8)),
        Member(84, "numSplitterCells", hkInt32),
        Member(96, "gravity", hkVector4),
        Member(112, "enableContactCaching", hkBool),
        Member(113, "mergeEventsBeforeDispatch", hkBool),
        Member(114, "leavingBroadPhaseBehavior", hkEnum(hknpWorldCinfoLeavingBroadPhaseBehavior, hkUint8)),
        Member(128, "broadPhaseAabb", hkAabb),
        Member(160, "broadPhaseConfig", Ptr(hknpBroadPhaseConfig)),
        Member(168, "collisionFilter", Ptr(hknpCollisionFilter)),
        Member(176, "shapeTagCodec", Ptr(hknpShapeTagCodec)),
        Member(184, "collisionTolerance", hkReal),
        Member(188, "relativeCollisionAccuracy", hkReal),
        Member(192, "enableWeldingForDefaultObjects", hkBool),
        Member(193, "enableWeldingForCriticalObjects", hkBool),
        Member(196, "solverTau", hkReal),
        Member(200, "solverDamp", hkReal),
        Member(204, "solverIterations", hkInt32),
        Member(208, "solverMicrosteps", hkInt32),
        Member(212, "defaultSolverTimestep", hkReal),
        Member(216, "maxApproachSpeedForHighQualitySolver", hkReal),
        Member(220, "enableDeactivation", hkBool),
        Member(221, "deleteCachesOnDeactivation", hkBool),
        Member(224, "largeIslandSize", hkInt32),
        Member(228, "enableSolverDynamicScheduling", hkBool),
        Member(232, "contactSolverType", hkInt32),
        Member(236, "unitScale", hkReal),
        Member(240, "applyUnitScaleToStaticConstants", hkBool),
    )
    members = local_members

    bodyBufferCapacity: int
    userBodyBuffer: None
    motionBufferCapacity: int
    userMotionBuffer: None
    constraintBufferCapacity: int
    userConstraintBuffer: None
    persistentStreamAllocator: None
    materialLibrary: hknpMaterialLibrary
    motionPropertiesLibrary: hknpMotionPropertiesLibrary
    qualityLibrary: hknpBodyQualityLibrary
    simulationType: int
    numSplitterCells: int
    gravity: hkVector4
    enableContactCaching: bool
    mergeEventsBeforeDispatch: bool
    leavingBroadPhaseBehavior: int
    broadPhaseAabb: hkAabb
    broadPhaseConfig: hknpBroadPhaseConfig
    collisionFilter: hknpCollisionFilter
    shapeTagCodec: hknpShapeTagCodec
    collisionTolerance: float
    relativeCollisionAccuracy: float
    enableWeldingForDefaultObjects: bool
    enableWeldingForCriticalObjects: bool
    solverTau: float
    solverDamp: float
    solverIterations: int
    solverMicrosteps: int
    defaultSolverTimestep: float
    maxApproachSpeedForHighQualitySolver: float
    enableDeactivation: bool
    deleteCachesOnDeactivation: bool
    largeIslandSize: int
    enableSolverDynamicScheduling: bool
    contactSolverType: int
    unitScale: float
    applyUnitScaleToStaticConstants: bool
