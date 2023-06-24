from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpWorldCinfoBroadPhaseType import hkpWorldCinfoBroadPhaseType
from .hkpWorldCinfoBroadPhaseBorderBehaviour import hkpWorldCinfoBroadPhaseBorderBehaviour
from .hkAabb import hkAabb
from .hkpCollisionFilter import hkpCollisionFilter
from .hkpConvexListFilter import hkpConvexListFilter
from .hkWorldMemoryAvailableWatchDog import hkWorldMemoryAvailableWatchDog
from .hkpWorldCinfoContactPointGeneration import hkpWorldCinfoContactPointGeneration
from .hkpWorldCinfoSimulationType import hkpWorldCinfoSimulationType


@dataclass(slots=True, eq=False, repr=False)
class hkpWorldCinfo(hkReferencedObject):
    alignment = 16
    byte_size = 256
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 18

    local_members = (
        Member(16, "gravity", hkVector4),
        Member(32, "broadPhaseQuerySize", hkInt32),
        Member(36, "contactRestingVelocity", hkReal),
        Member(40, "broadPhaseType", hkEnum(hkpWorldCinfoBroadPhaseType, hkInt8)),
        Member(41, "broadPhaseBorderBehaviour", hkEnum(hkpWorldCinfoBroadPhaseBorderBehaviour, hkInt8)),
        Member(42, "mtPostponeAndSortBroadPhaseBorderCallbacks", hkBool),
        Member(48, "broadPhaseWorldAabb", hkAabb),
        Member(80, "collisionTolerance", hkReal),
        Member(88, "collisionFilter", hkRefPtr(hkpCollisionFilter)),
        Member(96, "convexListFilter", hkRefPtr(hkpConvexListFilter)),
        Member(104, "expectedMaxLinearVelocity", hkReal),
        Member(108, "sizeOfToiEventQueue", _int),
        Member(112, "expectedMinPsiDeltaTime", hkReal),
        Member(120, "memoryWatchDog", hkRefPtr(hkWorldMemoryAvailableWatchDog)),
        Member(128, "broadPhaseNumMarkers", hkInt32),
        Member(132, "contactPointGeneration", hkEnum(hkpWorldCinfoContactPointGeneration, hkInt8)),
        Member(133, "allowToSkipConfirmedCallbacks", hkBool),
        Member(136, "solverTau", hkReal),
        Member(140, "solverDamp", hkReal),
        Member(144, "solverIterations", hkInt32),
        Member(148, "solverMicrosteps", hkInt32),
        Member(152, "maxConstraintViolation", hkReal),
        Member(156, "forceCoherentConstraintOrderingInSolver", hkBool),
        Member(160, "snapCollisionToConvexEdgeThreshold", hkReal),
        Member(164, "snapCollisionToConcaveEdgeThreshold", hkReal),
        Member(168, "enableToiWeldRejection", hkBool),
        Member(169, "enableDeprecatedWelding", hkBool),
        Member(172, "iterativeLinearCastEarlyOutDistance", hkReal),
        Member(176, "iterativeLinearCastMaxIterations", hkInt32),
        Member(180, "deactivationNumInactiveFramesSelectFlag0", hkUint8),
        Member(181, "deactivationNumInactiveFramesSelectFlag1", hkUint8),
        Member(182, "deactivationIntegrateCounter", hkUint8),
        Member(183, "shouldActivateOnRigidBodyTransformChange", hkBool),
        Member(184, "deactivationReferenceDistance", hkReal),
        Member(188, "toiCollisionResponseRotateNormal", hkReal),
        Member(192, "useCompoundSpuElf", hkBool),
        Member(196, "maxSectorsPerMidphaseCollideTask", _int),
        Member(200, "maxSectorsPerNarrowphaseCollideTask", _int),
        Member(204, "processToisMultithreaded", hkBool),
        Member(208, "maxEntriesPerToiMidphaseCollideTask", _int),
        Member(212, "maxEntriesPerToiNarrowphaseCollideTask", _int),
        Member(216, "maxNumToiCollisionPairsSinglethreaded", _int),
        Member(220, "numToisTillAllowedPenetrationSimplifiedToi", hkReal),
        Member(224, "numToisTillAllowedPenetrationToi", hkReal),
        Member(228, "numToisTillAllowedPenetrationToiHigher", hkReal),
        Member(232, "numToisTillAllowedPenetrationToiForced", hkReal),
        Member(236, "enableDeactivation", hkBool),
        Member(237, "simulationType", hkEnum(hkpWorldCinfoSimulationType, hkInt8)),
        Member(238, "enableSimulationIslands", hkBool),
        Member(240, "minDesiredIslandSize", hkUint32),
        Member(244, "processActionsInSingleThread", hkBool),
        Member(245, "allowIntegrationOfIslandsWithoutConstraintsInASeparateJob", hkBool),
        Member(248, "frameMarkerPsiSnap", hkReal),
        Member(252, "fireCollisionCallbacks", hkBool),
    )
    members = hkReferencedObject.members + local_members

    gravity: Vector4
    broadPhaseQuerySize: int
    contactRestingVelocity: float
    broadPhaseType: hkpWorldCinfoBroadPhaseType
    broadPhaseBorderBehaviour: hkpWorldCinfoBroadPhaseBorderBehaviour
    mtPostponeAndSortBroadPhaseBorderCallbacks: bool
    broadPhaseWorldAabb: hkAabb
    collisionTolerance: float
    collisionFilter: hkpCollisionFilter
    convexListFilter: hkpConvexListFilter
    expectedMaxLinearVelocity: float
    sizeOfToiEventQueue: int
    expectedMinPsiDeltaTime: float
    memoryWatchDog: hkWorldMemoryAvailableWatchDog
    broadPhaseNumMarkers: int
    contactPointGeneration: hkpWorldCinfoContactPointGeneration
    allowToSkipConfirmedCallbacks: bool
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
    useCompoundSpuElf: bool
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
    simulationType: hkpWorldCinfoSimulationType
    enableSimulationIslands: bool
    minDesiredIslandSize: int
    processActionsInSingleThread: bool
    allowIntegrationOfIslandsWithoutConstraintsInASeparateJob: bool
    frameMarkerPsiSnap: float
    fireCollisionCallbacks: bool
