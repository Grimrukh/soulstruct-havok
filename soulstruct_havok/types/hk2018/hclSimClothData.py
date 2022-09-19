from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hclSimClothDataOverridableSimulationInfo import hclSimClothDataOverridableSimulationInfo
from .hclSimClothDataParticleData import hclSimClothDataParticleData



from .hclSimClothPose import hclSimClothPose
from .hclConstraintSet import hclConstraintSet
from .hclSimClothDataCollidableTransformMap import hclSimClothDataCollidableTransformMap
from .hclCollidable import hclCollidable


from .hclAction import hclAction
from .hclSimClothDataTransferMotionData import hclSimClothDataTransferMotionData
from .hclSimClothDataLandscapeCollisionData import hclSimClothDataLandscapeCollisionData

from .hclSimClothDataCollidablePinchingData import hclSimClothDataCollidablePinchingData
from .hclVirtualCollisionPointsData import hclVirtualCollisionPointsData


class hclSimClothData(hkReferencedObject):
    alignment = 16
    byte_size = 736
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1395465018
    __version = 14

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "simulationInfo", hclSimClothDataOverridableSimulationInfo),
        Member(64, "particleDatas", hkArray(hclSimClothDataParticleData, hsh=3490937665)),
        Member(80, "fixedParticles", hkArray(hkUint16, hsh=3431155310)),
        Member(96, "doNormals", hkBool),
        Member(104, "simOpIds", hkArray(_unsigned_int, hsh=2115346695)),
        Member(120, "simClothPoses", hkArray(Ptr(hclSimClothPose, hsh=1847987427), hsh=3155674949)),
        Member(136, "staticConstraintSets", hkArray(Ptr(hclConstraintSet, hsh=479870377), hsh=3118140213)),
        Member(152, "antiPinchConstraintSets", hkArray(Ptr(hclConstraintSet, hsh=479870377), hsh=3118140213)),
        Member(168, "collidableTransformMap", hclSimClothDataCollidableTransformMap),
        Member(208, "perInstanceCollidables", hkArray(Ptr(hclCollidable, hsh=967513960), hsh=2769747279)),
        Member(224, "maxParticleRadius", hkReal),
        Member(232, "staticCollisionMasks", hkArray(hkUint32, hsh=1109639201)),
        Member(248, "actions", hkArray(Ptr(hclAction))),
        Member(264, "totalMass", hkReal),
        Member(268, "transferMotionData", hclSimClothDataTransferMotionData),
        Member(316, "transferMotionEnabled", hkBool),
        Member(317, "landscapeCollisionEnabled", hkBool),
        Member(320, "landscapeCollisionData", hclSimClothDataLandscapeCollisionData),
        Member(344, "numLandscapeCollidableParticles", hkUint32),
        Member(352, "triangleIndices", hkArray(hkUint16, hsh=3431155310)),
        Member(368, "triangleFlips", hkArray(hkUint8, hsh=2331026425)),
        Member(384, "pinchDetectionEnabled", hkBool),
        Member(392, "perParticlePinchDetectionEnabledFlags", hkArray(hkBool, hsh=3977017243)),
        Member(408, "collidablePinchingDatas", hkArray(hclSimClothDataCollidablePinchingData, hsh=3806523314)),
        Member(424, "minPinchedParticleIndex", hkUint16),
        Member(426, "maxPinchedParticleIndex", hkUint16),
        Member(428, "maxCollisionPairs", hkUint32),
        Member(432, "virtualCollisionPointsData", hclVirtualCollisionPointsData),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    simulationInfo: hclSimClothDataOverridableSimulationInfo
    particleDatas: list[hclSimClothDataParticleData]
    fixedParticles: list[int]
    doNormals: bool
    simOpIds: list[int]
    simClothPoses: list[hclSimClothPose]
    staticConstraintSets: list[hclConstraintSet]
    antiPinchConstraintSets: list[hclConstraintSet]
    collidableTransformMap: hclSimClothDataCollidableTransformMap
    perInstanceCollidables: list[hclCollidable]
    maxParticleRadius: float
    staticCollisionMasks: list[int]
    actions: list[hclAction]
    totalMass: float
    transferMotionData: hclSimClothDataTransferMotionData
    transferMotionEnabled: bool
    landscapeCollisionEnabled: bool
    landscapeCollisionData: hclSimClothDataLandscapeCollisionData
    numLandscapeCollidableParticles: int
    triangleIndices: list[int]
    triangleFlips: list[int]
    pinchDetectionEnabled: bool
    perParticlePinchDetectionEnabledFlags: list[bool]
    collidablePinchingDatas: list[hclSimClothDataCollidablePinchingData]
    minPinchedParticleIndex: int
    maxPinchedParticleIndex: int
    maxCollisionPairs: int
    virtualCollisionPointsData: hclVirtualCollisionPointsData
