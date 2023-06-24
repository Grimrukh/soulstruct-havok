from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hknpMaterialLibrary import hknpMaterialLibrary
from .hknpMotionPropertiesLibrary import hknpMotionPropertiesLibrary
from .hknpBodyQualityLibrary import hknpBodyQualityLibrary



from .hkAabb import hkAabb
from .hknpBroadPhaseConfig import hknpBroadPhaseConfig
from .hknpCollisionFilter import hknpCollisionFilter
from .hknpShapeTagCodec import hknpShapeTagCodec
from .hknpWeldingConfig import hknpWeldingConfig
from .hknpLodManagerCinfo import hknpLodManagerCinfo
from .hknpBodyIntegrator import hknpBodyIntegrator


@dataclass(slots=True, eq=False, repr=False)
class hknpWorldCinfo(hk):
    alignment = 16
    byte_size = 304
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 13

    local_members = (
        Member(0, "blockStreamAllocator", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(8, "bodyBufferCapacity", hkInt32),
        Member(16, "userBodyBuffer", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(24, "motionBufferCapacity", hkInt32),
        Member(32, "userMotionBuffer", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(40, "constraintBufferCapacity", hkInt32),
        Member(48, "userConstraintBuffer", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(56, "constraintGroupBufferCapacity", hkInt32),
        Member(64, "userConstraintGroupBuffer", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(72, "useBodyBacklinkBuffer", hkBool),
        Member(80, "materialLibrary", hkRefPtr(hknpMaterialLibrary)),
        Member(88, "motionPropertiesLibrary", hkRefPtr(hknpMotionPropertiesLibrary)),
        Member(96, "qualityLibrary", hkRefPtr(hknpBodyQualityLibrary)),
        Member(104, "simulationType", _unsigned_char),
        Member(108, "numSplitterCells", hkInt32),
        Member(112, "gravity", hkVector4),
        Member(128, "airDensity", hkReal),
        Member(132, "enableContactCaching", hkBool),
        Member(133, "mergeEventsBeforeDispatch", hkBool),
        Member(134, "broadPhaseType", _unsigned_char),
        Member(144, "broadPhaseAabb", hkAabb),
        Member(176, "broadPhaseConfig", hkRefPtr(hknpBroadPhaseConfig)),
        Member(184, "collisionFilter", hkRefPtr(hknpCollisionFilter)),
        Member(192, "shapeTagCodec", hkRefPtr(hknpShapeTagCodec)),
        Member(200, "collisionTolerance", hkReal),
        Member(204, "relativeCollisionAccuracy", hkReal),
        Member(208, "aabbMargin", hkReal),
        Member(212, "enableWeldingForDefaultObjects", hkBool),
        Member(213, "enableWeldingForCriticalObjects", hkBool),
        Member(216, "weldingConfig", hknpWeldingConfig),
        Member(220, "lodManagerCinfo", hknpLodManagerCinfo),
        Member(244, "enableSdfEdgeCollisions", hkBool),
        Member(245, "enableCollideWorkStealing", hkBool),
        Member(248, "particlesLandscapeQuadCacheSize", hkInt32),
        Member(252, "solverTau", hkReal),
        Member(256, "solverDamp", hkReal),
        Member(260, "solverIterations", hkInt32),
        Member(264, "solverMicrosteps", hkInt32),
        Member(268, "enableDeactivation", hkBool),
        Member(269, "enablePenetrationRecovery", hkBool),
        Member(272, "maxApproachSpeedForHighQualitySolver", hkReal),
        Member(280, "bodyIntegrator", hkRefPtr(hknpBodyIntegrator)),
        Member(288, "adjustSolverSettingsBasedOnTimestep", hkBool),
        Member(292, "expectedDeltaTime", hkReal),
        Member(296, "minSolverIterations", hkInt32),
        Member(300, "maxSolverIterations", hkInt32),
    )
    members = local_members

    blockStreamAllocator: hkReflectDetailOpaque
    bodyBufferCapacity: int
    userBodyBuffer: hkReflectDetailOpaque
    motionBufferCapacity: int
    userMotionBuffer: hkReflectDetailOpaque
    constraintBufferCapacity: int
    userConstraintBuffer: hkReflectDetailOpaque
    constraintGroupBufferCapacity: int
    userConstraintGroupBuffer: hkReflectDetailOpaque
    useBodyBacklinkBuffer: bool
    materialLibrary: hknpMaterialLibrary
    motionPropertiesLibrary: hknpMotionPropertiesLibrary
    qualityLibrary: hknpBodyQualityLibrary
    simulationType: int
    numSplitterCells: int
    gravity: Vector4
    airDensity: float
    enableContactCaching: bool
    mergeEventsBeforeDispatch: bool
    broadPhaseType: int
    broadPhaseAabb: hkAabb
    broadPhaseConfig: hknpBroadPhaseConfig
    collisionFilter: hknpCollisionFilter
    shapeTagCodec: hknpShapeTagCodec
    collisionTolerance: float
    relativeCollisionAccuracy: float
    aabbMargin: float
    enableWeldingForDefaultObjects: bool
    enableWeldingForCriticalObjects: bool
    weldingConfig: hknpWeldingConfig
    lodManagerCinfo: hknpLodManagerCinfo
    enableSdfEdgeCollisions: bool
    enableCollideWorkStealing: bool
    particlesLandscapeQuadCacheSize: int
    solverTau: float
    solverDamp: float
    solverIterations: int
    solverMicrosteps: int
    enableDeactivation: bool
    enablePenetrationRecovery: bool
    maxApproachSpeedForHighQualitySolver: float
    bodyIntegrator: hknpBodyIntegrator
    adjustSolverSettingsBasedOnTimestep: bool
    expectedDeltaTime: float
    minSolverIterations: int
    maxSolverIterations: int
