from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpWorldCinfoBroadPhaseBorderBehaviour import hkpWorldCinfoBroadPhaseBorderBehaviour
from .hkAabb import hkAabb
from .hkpWorldCinfoTreeUpdateType import hkpWorldCinfoTreeUpdateType
from .hkpCollisionFilter import hkpCollisionFilter
from .hkpConvexListFilter import hkpConvexListFilter
from .hkWorldMemoryAvailableWatchDog import hkWorldMemoryAvailableWatchDog
from .hkpWorldCinfoContactPointGeneration import hkpWorldCinfoContactPointGeneration
from .hkpWorldCinfoSimulationType import hkpWorldCinfoSimulationType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpWorldCinfo(hkReferencedObject):
    alignment = 16
    byte_size = 240
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "gravity", hkVector4),
        Member(32, "broadPhaseQuerySize", hkInt32),
        Member(36, "contactRestingVelocity", hkReal),
        Member(40, "broadPhaseBorderBehaviour", hkEnum(hkpWorldCinfoBroadPhaseBorderBehaviour, hkInt8)),
        Member(41, "mtPostponeAndSortBroadPhaseBorderCallbacks", hkBool),
        Member(48, "broadPhaseWorldAabb", hkAabb),
        Member(80, "useKdTree", hkBool),
        Member(81, "useMultipleTree", hkBool),
        Member(82, "treeUpdateType", hkEnum(hkpWorldCinfoTreeUpdateType, hkInt8)),
        Member(83, "autoUpdateKdTree", hkBool),
        Member(84, "collisionTolerance", hkReal),
        Member(88, "collisionFilter", Ptr(hkpCollisionFilter)),
        Member(92, "convexListFilter", Ptr(hkpConvexListFilter)),
        Member(96, "expectedMaxLinearVelocity", hkReal),
        Member(100, "sizeOfToiEventQueue", hkInt32),
        Member(104, "expectedMinPsiDeltaTime", hkReal),
        Member(108, "memoryWatchDog", Ptr(hkWorldMemoryAvailableWatchDog)),
        Member(112, "broadPhaseNumMarkers", hkInt32),
        Member(116, "contactPointGeneration", hkEnum(hkpWorldCinfoContactPointGeneration, hkInt8)),
        Member(117, "allowToSkipConfirmedCallbacks", hkBool),
        Member(118, "useHybridBroadphase", hkBool),
        Member(120, "solverTau", hkReal),
        Member(124, "solverDamp", hkReal),
        Member(128, "solverIterations", hkInt32),
        Member(132, "solverMicrosteps", hkInt32),
        Member(136, "maxConstraintViolation", hkReal),
        Member(140, "forceCoherentConstraintOrderingInSolver", hkBool),
        Member(144, "snapCollisionToConvexEdgeThreshold", hkReal),
        Member(148, "snapCollisionToConcaveEdgeThreshold", hkReal),
        Member(152, "enableToiWeldRejection", hkBool),
        Member(153, "enableDeprecatedWelding", hkBool),
        Member(156, "iterativeLinearCastEarlyOutDistance", hkReal),
        Member(160, "iterativeLinearCastMaxIterations", hkInt32),
        Member(164, "deactivationNumInactiveFramesSelectFlag0", hkUint8),
        Member(165, "deactivationNumInactiveFramesSelectFlag1", hkUint8),
        Member(166, "deactivationIntegrateCounter", hkUint8),
        Member(167, "shouldActivateOnRigidBodyTransformChange", hkBool),
        Member(168, "deactivationReferenceDistance", hkReal),
        Member(172, "toiCollisionResponseRotateNormal", hkReal),
        Member(176, "maxSectorsPerMidphaseCollideTask", hkInt32),
        Member(180, "maxSectorsPerNarrowphaseCollideTask", hkInt32),
        Member(184, "processToisMultithreaded", hkBool),
        Member(188, "maxEntriesPerToiMidphaseCollideTask", hkInt32),
        Member(192, "maxEntriesPerToiNarrowphaseCollideTask", hkInt32),
        Member(196, "maxNumToiCollisionPairsSinglethreaded", hkInt32),
        Member(200, "numToisTillAllowedPenetrationSimplifiedToi", hkReal),
        Member(204, "numToisTillAllowedPenetrationToi", hkReal),
        Member(208, "numToisTillAllowedPenetrationToiHigher", hkReal),
        Member(212, "numToisTillAllowedPenetrationToiForced", hkReal),
        Member(216, "enableDeactivation", hkBool),
        Member(217, "simulationType", hkEnum(hkpWorldCinfoSimulationType, hkInt8)),
        Member(218, "enableSimulationIslands", hkBool),
        Member(220, "minDesiredIslandSize", hkUint32),
        Member(224, "processActionsInSingleThread", hkBool),
        Member(225, "allowIntegrationOfIslandsWithoutConstraintsInASeparateJob", hkBool),
        Member(228, "frameMarkerPsiSnap", hkReal),
        Member(232, "fireCollisionCallbacks", hkBool),
    )
    members = hkReferencedObject.members + local_members

    gravity: Vector4
    broadPhaseQuerySize: int
    contactRestingVelocity: float
    broadPhaseBorderBehaviour: int
    mtPostponeAndSortBroadPhaseBorderCallbacks: bool
    broadPhaseWorldAabb: hkAabb
    useKdTree: bool
    useMultipleTree: bool
    treeUpdateType: int
    autoUpdateKdTree: bool
    collisionTolerance: float
    collisionFilter: hkpCollisionFilter
    convexListFilter: hkpConvexListFilter
    expectedMaxLinearVelocity: float
    sizeOfToiEventQueue: int
    expectedMinPsiDeltaTime: float
    memoryWatchDog: hkWorldMemoryAvailableWatchDog
    broadPhaseNumMarkers: int
    contactPointGeneration: int
    allowToSkipConfirmedCallbacks: bool
    useHybridBroadphase: bool
    solverTau: float
    solverDamp: float
    solverIterations: int
    solverMicrosteps: int
    maxConstraintViolation: float
    forceCoherentConstraintOrderingInSolver: bool
    snapCollisionToConvexEdgeThreshold: float
    snapCollisionToConcaveEdgeThreshold: float
    enableToiWeldRejection: bool
    enableDeprecatedWelding: bool
    iterativeLinearCastEarlyOutDistance: float
    iterativeLinearCastMaxIterations: int
    deactivationNumInactiveFramesSelectFlag0: int
    deactivationNumInactiveFramesSelectFlag1: int
    deactivationIntegrateCounter: int
    shouldActivateOnRigidBodyTransformChange: bool
    deactivationReferenceDistance: float
    toiCollisionResponseRotateNormal: float
    maxSectorsPerMidphaseCollideTask: int
    maxSectorsPerNarrowphaseCollideTask: int
    processToisMultithreaded: bool
    maxEntriesPerToiMidphaseCollideTask: int
    maxEntriesPerToiNarrowphaseCollideTask: int
    maxNumToiCollisionPairsSinglethreaded: int
    numToisTillAllowedPenetrationSimplifiedToi: float
    numToisTillAllowedPenetrationToi: float
    numToisTillAllowedPenetrationToiHigher: float
    numToisTillAllowedPenetrationToiForced: float
    enableDeactivation: bool
    simulationType: int
    enableSimulationIslands: bool
    minDesiredIslandSize: int
    processActionsInSingleThread: bool
    allowIntegrationOfIslandsWithoutConstraintsInASeparateJob: bool
    frameMarkerPsiSnap: float
    fireCollisionCallbacks: bool
