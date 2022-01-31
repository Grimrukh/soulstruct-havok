"""Auto-generated types for Havok 2014.

Generated from files:
    c1430.HKX
"""
from __future__ import annotations

from soulstruct_havok.enums import TagDataType, MemberFlags
from soulstruct_havok.types.core import *
from soulstruct_havok.types.hk2014_base import *


# --- Invalid Types --- #


# --- Primitive Types --- #


# --- Havok Struct Types --- #


# --- Havok Wrappers --- #


# --- Havok Core Types --- #


class hkaBone(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "lockTranslation", hkBool),
    )
    members = local_members

    name: str
    lockTranslation: bool


class hkLocalFrame(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkaSkeletonPartition(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "startBoneIndex", hkInt16),
        Member(10, "numBones", hkInt16),
    )
    members = local_members

    name: str
    startBoneIndex: int
    numBones: int


class hkaAnnotationTrackAnnotation(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "time", hkReal),
        Member(8, "text", hkStringPtr),
    )
    members = local_members

    time: float
    text: str


class hkaBoneAttachment(hkReferencedObject):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(16, "originalSkeletonName", hkStringPtr),
        Member(32, "boneFromAttachment", hkMatrix4),
        Member(96, "attachment", Ptr(hkReferencedObject)),
        Member(104, "name", hkStringPtr),
        Member(112, "boneIndex", hkInt16),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    boneFromAttachment: hkMatrix4
    attachment: hkReferencedObject
    name: str
    boneIndex: int


class hkxVertexBufferVertexData(hk):
    alignment = 16
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(0, "vectorData", hkArray(hkUint32)),
        Member(16, "floatData", hkArray(hkUint32)),
        Member(32, "uint32Data", hkArray(hkUint32)),
        Member(48, "uint16Data", hkArray(hkUint16)),
        Member(64, "uint8Data", hkArray(hkUint8)),
        Member(80, "numVerts", hkUint32),
        Member(84, "vectorStride", hkUint32),
        Member(88, "floatStride", hkUint32),
        Member(92, "uint32Stride", hkUint32),
        Member(96, "uint16Stride", hkUint32),
        Member(100, "uint8Stride", hkUint32),
    )
    members = local_members

    vectorData: list[int]
    floatData: list[int]
    uint32Data: list[int]
    uint16Data: list[int]
    uint8Data: list[int]
    numVerts: int
    vectorStride: int
    floatStride: int
    uint32Stride: int
    uint16Stride: int
    uint8Stride: int


class hkxAttribute(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "value", Ptr(hkReferencedObject)),
    )
    members = local_members

    name: str
    value: hkReferencedObject


class hkxMaterialProperty(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "key", hkUint32),
        Member(4, "value", hkUint32),
    )
    members = local_members

    key: int
    value: int


class hkMeshBoneIndexMapping(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "mapping", hkArray(hkInt16)),
    )
    members = local_members

    mapping: list[int]


class hkaMeshBindingMapping(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "mapping", hkArray(hkInt16)),
    )
    members = local_members

    mapping: list[int]


class hkCompressedMassProperties(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "centerOfMass", hkStruct(hkInt16, 4)),
        Member(8, "inertia", hkStruct(hkInt16, 4)),
        Member(16, "majorAxisSpace", hkStruct(hkInt16, 4)),
        Member(24, "mass", hkReal),
        Member(28, "volume", hkReal),
    )
    members = local_members

    centerOfMass: tuple[int, ...]
    inertia: tuple[int, ...]
    majorAxisSpace: tuple[int, ...]
    mass: float
    volume: float


class hkRefCountedPropertiesEntry(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "object", Ptr(hkReferencedObject)),
        Member(8, "key", hkUint16),
        Member(10, "flags", hkUint16),
    )
    members = local_members

    object: hkReferencedObject
    key: int
    flags: int


class hknpConvexPolytopeShapeFace(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "firstIndex", hkUint16),
        Member(2, "numIndices", hkUint8),
        Member(3, "minHalfAngle", hkUint8),
    )
    members = local_members

    firstIndex: int
    numIndices: int
    minHalfAngle: int


class hkpConstraintData(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "userData", hkUlong),
    )
    members = hkReferencedObject.members + local_members

    userData: int


class hknpSurfaceVelocity(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hknpMotionProperties(hk):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(0, "isExclusive", hkUint32),
        Member(4, "flags", hkFlags(hkUint32)),
        Member(8, "gravityFactor", hkReal),
        Member(12, "timeFactor", hkReal),
        Member(16, "maxLinearSpeed", hkReal),
        Member(20, "maxAngularSpeed", hkReal),
        Member(24, "linearDamping", hkReal),
        Member(28, "angularDamping", hkReal),
        Member(32, "solverStabilizationSpeedThreshold", hkReal),
        Member(36, "solverStabilizationSpeedReduction", hkReal),
        Member(40, "maxDistSqrd", hkReal),
        Member(44, "maxRotSqrd", hkReal),
        Member(48, "invBlockSize", hkReal),
        Member(52, "pathingUpperThreshold", hkInt16),
        Member(54, "pathingLowerThreshold", hkInt16),
        Member(56, "numDeactivationFrequencyPasses", hkUint8),
        Member(57, "deactivationVelocityScaleSquare", hkUint8),
        Member(58, "minimumPathingVelocityScaleSquare", hkUint8),
        Member(59, "spikingVelocityScaleThresholdSquared", hkUint8),
        Member(60, "minimumSpikingVelocityScaleSquared", hkUint8),
    )
    members = local_members

    isExclusive: int
    flags: int
    gravityFactor: float
    timeFactor: float
    maxLinearSpeed: float
    maxAngularSpeed: float
    linearDamping: float
    angularDamping: float
    solverStabilizationSpeedThreshold: float
    solverStabilizationSpeedReduction: float
    maxDistSqrd: float
    maxRotSqrd: float
    invBlockSize: float
    pathingUpperThreshold: int
    pathingLowerThreshold: int
    numDeactivationFrequencyPasses: int
    deactivationVelocityScaleSquare: int
    minimumPathingVelocityScaleSquare: int
    spikingVelocityScaleThresholdSquared: int
    minimumSpikingVelocityScaleSquared: int


class hknpMotionCinfo(hk):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "motionPropertiesId", hkUint16),
        Member(2, "enableDeactivation", hkBool),
        Member(4, "inverseMass", hkReal),
        Member(8, "massFactor", hkReal),
        Member(12, "maxLinearAccelerationDistancePerStep", hkReal),
        Member(16, "maxRotationToPreventTunneling", hkReal),
        Member(32, "inverseInertiaLocal", hkVector4),
        Member(48, "centerOfMassWorld", hkVector4),
        Member(64, "orientation", hkQuaternionf),
        Member(80, "linearVelocity", hkVector4),
        Member(96, "angularVelocity", hkVector4),
    )
    members = local_members

    motionPropertiesId: int
    enableDeactivation: bool
    inverseMass: float
    massFactor: float
    maxLinearAccelerationDistancePerStep: float
    maxRotationToPreventTunneling: float
    inverseInertiaLocal: hkVector4
    centerOfMassWorld: hkVector4
    orientation: hkQuaternionf
    linearVelocity: hkVector4
    angularVelocity: hkVector4


class hknpConstraintCinfo(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(0, "constraintData", Ptr(hkpConstraintData)),
        Member(8, "bodyA", hkUint32),
        Member(12, "bodyB", hkUint32),
        Member(16, "flags", hkFlags(hkUint8)),
    )
    members = local_members

    constraintData: hkpConstraintData
    bodyA: int
    bodyB: int
    flags: int


class hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "elements", hkArray(hknpMotionProperties)),
        Member(16, "firstFree", hkInt32),
    )
    members = local_members

    elements: list[hknpMotionProperties]
    firstFree: int


class hknpBodyQuality(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "priority", hkInt32),
        Member(4, "supportedFlags", hkFlags(hkUint32)),
        Member(8, "requestedFlags", hkFlags(hkUint32)),
        Member(12, "contactCachingRelativeMovementThreshold", hkReal),
    )
    members = local_members

    priority: int
    supportedFlags: int
    requestedFlags: int
    contactCachingRelativeMovementThreshold: float


class hkAabb(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "min", hkVector4),
        Member(16, "max", hkVector4),
    )
    members = local_members

    min: hkVector4
    max: hkVector4


class hknpBroadPhaseConfig(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkaSkeletonMapperDataPartitionMappingRange(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "startMappingIndex", hkInt32),
        Member(4, "numMappings", hkInt32),
    )
    members = local_members

    startMappingIndex: int
    numMappings: int


class hkaSkeletonMapperDataSimpleMapping(hk):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "boneA", hkInt16),
        Member(2, "boneB", hkInt16),
        Member(16, "aFromBTransform", hkQsTransform),
    )
    members = local_members

    boneA: int
    boneB: int
    aFromBTransform: hkQsTransform


class hkaSkeletonMapperDataChainMapping(hk):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "startBoneA", hkInt16),
        Member(2, "endBoneA", hkInt16),
        Member(4, "startBoneB", hkInt16),
        Member(6, "endBoneB", hkInt16),
        Member(16, "startAFromBTransform", hkQsTransform),
        Member(64, "endAFromBTransform", hkQsTransform),
    )
    members = local_members

    startBoneA: int
    endBoneA: int
    startBoneB: int
    endBoneB: int
    startAFromBTransform: hkQsTransform
    endAFromBTransform: hkQsTransform


class hkRootLevelContainerNamedVariant(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "className", hkStringPtr),
        Member(16, "variant", Ptr(hkReferencedObject)),
    )
    members = local_members

    name: str
    className: str
    variant: hkReferencedObject


class hkaAnimationAnimationType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32
    __real_name = "hkaAnimation::AnimationType"
    local_members = ()


class hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkaAnimatedReferenceFrame::hkaReferenceFrameTypeEnum"
    local_members = ()


class hkaAnimationBindingBlendHint(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkaAnimationBinding::BlendHint"
    local_members = ()


class hkxVertexDescriptionElementDeclDataType(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16
    __real_name = "hkxVertexDescriptionElementDecl::DataType"
    local_members = ()


class hkxVertexDescriptionElementDeclDataUsage(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16
    __real_name = "hkxVertexDescriptionElementDecl::DataUsage"
    local_members = ()


class hkxIndexBufferIndexType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkxIndexBuffer::IndexType"
    local_members = ()


class hkxMaterialUVMappingAlgorithm(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.Int32
    __real_name = "hkxMaterial::UVMappingAlgorithm"
    local_members = ()


class hkxMaterialTransparency(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hkxMaterial::Transparency"
    local_members = ()


class hkxMaterialTextureStageTextureType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32
    __real_name = "hkxMaterialTextureStage::TextureType"
    local_members = ()


class hkxVertexAnimationUsageMapDataUsage(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16
    __real_name = "hkxVertexAnimationUsageMap::DataUsage"
    local_members = ()


class hknpShapeEnum(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hknpShape::Enum"
    local_members = ()


class hkpConstraintMotorMotorType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkpConstraintMotor::MotorType"
    local_members = ()


class hkpConstraintAtomAtomType(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16
    __real_name = "hkpConstraintAtom::AtomType"
    local_members = ()


class hkpConeLimitConstraintAtomMeasurementMode(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hkpConeLimitConstraintAtom::MeasurementMode"
    local_members = ()


class hkpBallSocketConstraintAtomSolvingMethod(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hkpBallSocketConstraintAtom::SolvingMethod"
    local_members = ()


class hknpMaterialTriggerType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hknpMaterial::TriggerType"
    local_members = ()


class hknpMaterialCombinePolicy(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hknpMaterial::CombinePolicy"
    local_members = ()


class hknpMaterialMassChangerCategory(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hknpMaterial::MassChangerCategory"
    local_members = ()


class hknpWorldCinfoSimulationType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hknpWorldCinfo::SimulationType"
    local_members = ()


class hknpWorldCinfoLeavingBroadPhaseBehavior(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hknpWorldCinfo::LeavingBroadPhaseBehavior"
    local_members = ()


class hknpCollisionFilterType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hknpCollisionFilter::Type"
    local_members = ()


class hknpShapeTagCodecType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hknpShapeTagCodec::Type"
    local_members = ()


class hkaSkeletonMapperDataMappingType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32
    __real_name = "hkaSkeletonMapperData::MappingType"
    local_members = ()


class hkaSkeletonLocalFrameOnBone(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "localFrame", Ptr(hkLocalFrame)),
        Member(8, "boneIndex", hkInt16),
    )
    members = local_members

    localFrame: hkLocalFrame
    boneIndex: int


class hkaAnimatedReferenceFrame(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(
            16,
            "frameType",
            hkEnum(hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum, hkInt8),
            MemberFlags.NotSerializable,
        ),
    )
    members = hkReferencedObject.members + local_members

    frameType: int


class hkaAnnotationTrack(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "trackName", hkStringPtr),
        Member(8, "annotations", hkArray(hkaAnnotationTrackAnnotation)),
    )
    members = local_members

    trackName: str
    annotations: list[hkaAnnotationTrackAnnotation]


class hkxVertexDescriptionElementDecl(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 4

    local_members = (
        Member(0, "byteOffset", hkUint32),
        Member(4, "type", hkEnum(hkxVertexDescriptionElementDeclDataType, hkUint16)),
        Member(6, "usage", hkEnum(hkxVertexDescriptionElementDeclDataUsage, hkUint16)),
        Member(8, "byteStride", hkUint32),
        Member(12, "numElements", hkUint8),
        Member(16, "channelID", hkStringPtr),
    )
    members = local_members

    byteOffset: int
    type: int
    usage: int
    byteStride: int
    numElements: int
    channelID: str


class hkxIndexBuffer(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(16, "indexType", hkEnum(hkxIndexBufferIndexType, hkInt8)),
        Member(24, "indices16", hkArray(hkUint16)),
        Member(40, "indices32", hkArray(hkUint32)),
        Member(56, "vertexBaseOffset", hkUint32),
        Member(60, "length", hkUint32),
    )
    members = hkReferencedObject.members + local_members

    indexType: int
    indices16: list[int]
    indices32: list[int]
    vertexBaseOffset: int
    length: int


class hkxAttributeGroup(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "attributes", hkArray(hkxAttribute)),
    )
    members = local_members

    name: str
    attributes: list[hkxAttribute]


class hkxMaterialTextureStage(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "texture", Ptr(hkReferencedObject)),
        Member(8, "usageHint", hkEnum(hkxMaterialTextureStageTextureType, hkInt32)),
        Member(12, "tcoordChannel", hkInt32),
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: int
    tcoordChannel: int


class hkxVertexAnimationUsageMap(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "use", hkEnum(hkxVertexAnimationUsageMapDataUsage, hkUint16)),
        Member(2, "useIndexOrig", hkUint8),
        Member(3, "useIndexLocal", hkUint8),
    )
    members = local_members

    use: int
    useIndexOrig: int
    useIndexLocal: int


class hknpShapeMassProperties(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3910735656

    local_members = (
        Member(16, "compressedMassProperties", hkCompressedMassProperties),
    )
    members = hkReferencedObject.members + local_members

    compressedMassProperties: hkCompressedMassProperties


class hkRefCountedProperties(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2086094951
    __version = 1

    local_members = (
        Member(0, "entries", hkArray(hkRefCountedPropertiesEntry)),
    )
    members = local_members

    entries: list[hkRefCountedPropertiesEntry]


class hknpShape(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(16, "flags", hkFlags(hkUint16)),
        Member(18, "numShapeKeyBits", hkUint8),
        Member(19, "dispatchType", hkEnum(hknpShapeEnum, hkUint8)),
        Member(20, "convexRadius", hkReal),
        Member(24, "userData", hkUint64),
        Member(32, "properties", Ptr(hkRefCountedProperties)),
    )
    members = hkReferencedObject.members + local_members

    flags: int
    numShapeKeyBits: int
    dispatchType: int
    convexRadius: float
    userData: int
    properties: hkRefCountedProperties


class hkpConstraintMotor(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "type", hkEnum(hkpConstraintMotorMotorType, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    type: int


class hkpConstraintAtom(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "type", hkEnum(hkpConstraintAtomAtomType, hkUint16)),
    )
    members = local_members

    type: int


class hkpSetupStabilizationAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(2, "enabled", hkBool),
        Member(3, "padding", hkStruct(hkUint8, 1), MemberFlags.NotSerializable),
        Member(4, "maxLinImpulse", hkReal),
        Member(8, "maxAngImpulse", hkReal),
        Member(12, "maxAngle", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    enabled: bool
    padding: tuple[int, ...]
    maxLinImpulse: float
    maxAngImpulse: float
    maxAngle: float


class hkpRagdollMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(2, "isEnabled", hkBool),
        Member(4, "initializedOffset", hkInt16, MemberFlags.NotSerializable),
        Member(6, "previousTargetAnglesOffset", hkInt16, MemberFlags.NotSerializable),
        Member(16, "target_bRca", hkMatrix3),
        Member(64, "motors", hkStruct(Ptr(hkpConstraintMotor), 3)),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: bool
    initializedOffset: int
    previousTargetAnglesOffset: int
    target_bRca: hkMatrix3
    motors: tuple[hkpConstraintMotor, ...]


class hkpAngFrictionConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "firstFrictionAxis", hkUint8),
        Member(4, "numFrictionAxes", hkUint8),
        Member(8, "maxFrictionTorque", hkReal),
        Member(12, "padding", hkStruct(hkUint8, 4), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    firstFrictionAxis: int
    numFrictionAxes: int
    maxFrictionTorque: float
    padding: tuple[int, ...]


class hkpTwistLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "twistAxis", hkUint8),
        Member(4, "refAxis", hkUint8),
        Member(8, "minAngle", hkReal),
        Member(12, "maxAngle", hkReal),
        Member(16, "angularLimitsTauFactor", hkReal),
        Member(20, "padding", hkStruct(hkUint8, 12), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    twistAxis: int
    refAxis: int
    minAngle: float
    maxAngle: float
    angularLimitsTauFactor: float
    padding: tuple[int, ...]


class hkpConeLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "twistAxisInA", hkUint8),
        Member(4, "refAxisInB", hkUint8),
        Member(5, "angleMeasurementMode", hkEnum(hkpConeLimitConstraintAtomMeasurementMode, hkUint8)),
        Member(6, "memOffsetToAngleOffset", hkUint8),
        Member(8, "minAngle", hkReal),
        Member(12, "maxAngle", hkReal),
        Member(16, "angularLimitsTauFactor", hkReal),
        Member(20, "padding", hkStruct(hkUint8, 12), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    twistAxisInA: int
    refAxisInB: int
    angleMeasurementMode: int
    memOffsetToAngleOffset: int
    minAngle: float
    maxAngle: float
    angularLimitsTauFactor: float
    padding: tuple[int, ...]


class hkpBallSocketConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 5

    local_members = (
        Member(2, "solvingMethod", hkEnum(hkpBallSocketConstraintAtomSolvingMethod, hkUint8)),
        Member(3, "bodiesToNotify", hkUint8),
        Member(4, "velocityStabilizationFactor", hkUFloat8),
        Member(5, "enableLinearImpulseLimit", hkBool),
        Member(8, "breachImpulse", hkReal),
        Member(12, "inertiaStabilizationFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    solvingMethod: int
    bodiesToNotify: int
    velocityStabilizationFactor: hkUFloat8
    enableLinearImpulseLimit: bool
    breachImpulse: float
    inertiaStabilizationFactor: float


class hkpAngMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(2, "isEnabled", hkBool),
        Member(3, "motorAxis", hkUint8),
        Member(4, "initializedOffset", hkInt16, MemberFlags.NotSerializable),
        Member(6, "previousTargetAngleOffset", hkInt16, MemberFlags.NotSerializable),
        Member(8, "correspondingAngLimitSolverResultOffset", hkInt16, MemberFlags.NotSerializable),
        Member(12, "targetAngle", hkReal),
        Member(16, "motor", Ptr(hkpConstraintMotor)),
        Member(24, "padding", hkStruct(hkUint8, 12), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: bool
    motorAxis: int
    initializedOffset: int
    previousTargetAngleOffset: int
    correspondingAngLimitSolverResultOffset: int
    targetAngle: float
    motor: hkpConstraintMotor
    padding: tuple[int, ...]


class hkpAngLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "limitAxis", hkUint8),
        Member(4, "minAngle", hkReal),
        Member(8, "maxAngle", hkReal),
        Member(12, "angularLimitsTauFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    limitAxis: int
    minAngle: float
    maxAngle: float
    angularLimitsTauFactor: float


class hkp2dAngConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "freeRotationAxis", hkUint8),
        Member(3, "padding", hkStruct(hkUint8, 12), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    freeRotationAxis: int
    padding: tuple[int, ...]


class hknpMaterial(hk):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "isExclusive", hkUint32),
        Member(12, "flags", hkInt32),
        Member(16, "triggerType", hkEnum(hknpMaterialTriggerType, hkUint8)),
        Member(17, "triggerManifoldTolerance", hkUFloat8),
        Member(18, "dynamicFriction", hkHalf16),
        Member(20, "staticFriction", hkHalf16),
        Member(22, "restitution", hkHalf16),
        Member(24, "frictionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8)),
        Member(25, "restitutionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8)),
        Member(26, "weldingTolerance", hkHalf16),
        Member(28, "maxContactImpulse", hkReal),
        Member(32, "fractionOfClippedImpulseToApply", hkReal),
        Member(36, "massChangerCategory", hkEnum(hknpMaterialMassChangerCategory, hkUint8)),
        Member(38, "massChangerHeavyObjectFactor", hkHalf16),
        Member(40, "softContactForceFactor", hkHalf16),
        Member(42, "softContactDampFactor", hkHalf16),
        Member(44, "softContactSeperationVelocity", hkUFloat8),
        Member(48, "surfaceVelocity", Ptr(hknpSurfaceVelocity)),
        Member(56, "disablingCollisionsBetweenCvxCvxDynamicObjectsDistance", hkHalf16),
        Member(64, "userData", hkUint64),
        Member(72, "isShared", hkBool),
    )
    members = local_members

    name: str
    isExclusive: int
    flags: int
    triggerType: int
    triggerManifoldTolerance: hkUFloat8
    dynamicFriction: hkHalf16
    staticFriction: hkHalf16
    restitution: hkHalf16
    frictionCombinePolicy: int
    restitutionCombinePolicy: int
    weldingTolerance: hkHalf16
    maxContactImpulse: float
    fractionOfClippedImpulseToApply: float
    massChangerCategory: int
    massChangerHeavyObjectFactor: hkHalf16
    softContactForceFactor: hkHalf16
    softContactDampFactor: hkHalf16
    softContactSeperationVelocity: hkUFloat8
    surfaceVelocity: hknpSurfaceVelocity
    disablingCollisionsBetweenCvxCvxDynamicObjectsDistance: hkHalf16
    userData: int
    isShared: bool


class hknpBodyCinfo(hk):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(0, "shape", Ptr(hknpShape)),
        Member(8, "reservedBodyId", hkUint32),
        Member(12, "motionId", hkUint32),
        Member(16, "qualityId", hkUint8),
        Member(18, "materialId", hkUint16),
        Member(20, "collisionFilterInfo", hkUint32),
        Member(24, "flags", hkInt32),
        Member(28, "collisionLookAheadDistance", hkReal),
        Member(32, "name", hkStringPtr),
        Member(40, "userData", hkUint64),
        Member(48, "position", hkVector4),
        Member(64, "orientation", hkQuaternionf),
        Member(80, "spuFlags", hkFlags(hkUint8)),
        Member(88, "localFrame", Ptr(hkLocalFrame)),
    )
    members = local_members

    shape: hknpShape
    reservedBodyId: int
    motionId: int
    qualityId: int
    materialId: int
    collisionFilterInfo: int
    flags: int
    collisionLookAheadDistance: float
    name: str
    userData: int
    position: hkVector4
    orientation: hkQuaternionf
    spuFlags: int
    localFrame: hkLocalFrame


class hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "elements", hkArray(hknpMaterial)),
        Member(16, "firstFree", hkInt32),
    )
    members = local_members

    elements: list[hknpMaterial]
    firstFree: int


class hknpMotionPropertiesLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "entryAddedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(24, "entryModifiedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "entryRemovedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(
            40,
            "entries",
            hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations,
        ),
    )
    members = hkReferencedObject.members + local_members

    entryAddedSignal: None
    entryModifiedSignal: None
    entryRemovedSignal: None
    entries: hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations


class hknpBodyQualityLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 544
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "qualityModifiedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "qualities", hkStruct(hknpBodyQuality, 32)),
    )
    members = hkReferencedObject.members + local_members

    qualityModifiedSignal: None
    qualities: tuple[hknpBodyQuality, ...]


class hknpCollisionFilter(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "type", hkEnum(hknpCollisionFilterType, hkUint8)),
    )
    members = hkReferencedObject.members + local_members

    type: int


class hknpShapeTagCodec(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(16, "type", hkEnum(hknpShapeTagCodecType, hkUint8)),
    )
    members = hkReferencedObject.members + local_members

    type: int


class hkRootLevelContainer(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 661831966

    local_members = (
        Member(0, "namedVariants", hkArray(hkRootLevelContainerNamedVariant)),
    )
    members = local_members

    namedVariants: list[hkRootLevelContainerNamedVariant]


class hkaSkeleton(hkReferencedObject):
    alignment = 16
    byte_size = 136
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4274114267
    __version = 5

    local_members = (
        Member(16, "name", hkStringPtr),
        Member(24, "parentIndices", hkArray(hkInt16)),
        Member(40, "bones", hkArray(hkaBone)),
        Member(56, "referencePose", hkArray(hkQsTransform)),
        Member(72, "referenceFloats", hkArray(hkReal)),
        Member(88, "floatSlots", hkArray(hkStringPtr)),
        Member(104, "localFrames", hkArray(hkaSkeletonLocalFrameOnBone)),
        Member(120, "partitions", hkArray(hkaSkeletonPartition)),
    )
    members = hkReferencedObject.members + local_members

    name: str
    parentIndices: list[int]
    bones: list[hkaBone]
    referencePose: list[hkQsTransform]
    referenceFloats: list[float]
    floatSlots: list[str]
    localFrames: list[hkaSkeletonLocalFrameOnBone]
    partitions: list[hkaSkeletonPartition]


class hkaAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(16, "type", hkEnum(hkaAnimationAnimationType, hkInt32)),
        Member(20, "duration", hkReal),
        Member(24, "numberOfTransformTracks", hkInt32),
        Member(28, "numberOfFloatTracks", hkInt32),
        Member(32, "extractedMotion", Ptr(hkaAnimatedReferenceFrame)),
        Member(40, "annotationTracks", hkArray(hkaAnnotationTrack)),
    )
    members = hkReferencedObject.members + local_members

    type: int
    duration: float
    numberOfTransformTracks: int
    numberOfFloatTracks: int
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]


class hkaAnimationBinding(hkReferencedObject):
    alignment = 16
    byte_size = 88
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(16, "originalSkeletonName", hkStringPtr),
        Member(24, "animation", Ptr(hkaAnimation)),
        Member(32, "transformTrackToBoneIndices", hkArray(hkInt16)),
        Member(48, "floatTrackToFloatSlotIndices", hkArray(hkInt16)),
        Member(64, "partitionIndices", hkArray(hkInt16)),
        Member(80, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    animation: hkaAnimation
    transformTrackToBoneIndices: list[int]
    floatTrackToFloatSlotIndices: list[int]
    partitionIndices: list[int]
    blendHint: int


class hkxVertexDescription(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "decls", hkArray(hkxVertexDescriptionElementDecl)),
    )
    members = local_members

    decls: list[hkxVertexDescriptionElementDecl]


class hkxAttributeHolder(hkReferencedObject):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(16, "attributeGroups", hkArray(hkxAttributeGroup)),
    )
    members = hkReferencedObject.members + local_members

    attributeGroups: list[hkxAttributeGroup]


class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(32, "name", hkStringPtr),
        Member(40, "className", hkStringPtr),
    )
    members = hkxAttributeHolder.members + local_members

    name: str
    className: str


class hknpConvexShape(hknpShape):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(48, "vertices", hkRelArray(hkVector4)),
    )
    members = hknpShape.members + local_members

    vertices: list[hkVector4]


class hkpLimitedForceConstraintMotor(hkpConstraintMotor):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(24, "minForce", hkReal),
        Member(28, "maxForce", hkReal),
    )
    members = hkpConstraintMotor.members + local_members

    minForce: float
    maxForce: float


class hkpSetLocalTransformsConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "transformA", hkTransform),
        Member(80, "transformB", hkTransform),
    )
    members = hkpConstraintAtom.members + local_members

    transformA: hkTransform
    transformB: hkTransform


class hkpLimitedHingeConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 272
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom),
        Member(160, "angMotor", hkpAngMotorConstraintAtom),
        Member(200, "angFriction", hkpAngFrictionConstraintAtom),
        Member(216, "angLimit", hkpAngLimitConstraintAtom),
        Member(232, "2dAng", hkp2dAngConstraintAtom),
        Member(248, "ballSocket", hkpBallSocketConstraintAtom),
    )
    members = local_members

    transforms: hkpSetLocalTransformsConstraintAtom
    setupStabilization: hkpSetupStabilizationAtom
    angMotor: hkpAngMotorConstraintAtom
    angFriction: hkpAngFrictionConstraintAtom
    angLimit: hkpAngLimitConstraintAtom
    ballSocket: hkpBallSocketConstraintAtom


class hknpPhysicsSystemData(hkReferencedObject):
    alignment = 16
    byte_size = 120
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "materials", hkArray(hknpMaterial)),
        Member(32, "motionProperties", hkArray(hknpMotionProperties)),
        Member(48, "motionCinfos", hkArray(hknpMotionCinfo)),
        Member(64, "bodyCinfos", hkArray(hknpBodyCinfo)),
        Member(80, "constraintCinfos", hkArray(hknpConstraintCinfo)),
        Member(96, "referencedObjects", hkArray(Ptr(hkReferencedObject))),
        Member(112, "name", hkStringPtr),
    )
    members = hkReferencedObject.members + local_members

    materials: list[hknpMaterial]
    motionProperties: list[hknpMotionProperties]
    motionCinfos: list[hknpMotionCinfo]
    bodyCinfos: list[hknpBodyCinfo]
    constraintCinfos: list[hknpConstraintCinfo]
    referencedObjects: list[hkReferencedObject]
    name: str


class hknpMaterialLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "materialAddedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(24, "materialModifiedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "materialRemovedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(40, "entries", hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations),
    )
    members = hkReferencedObject.members + local_members

    materialAddedSignal: None
    materialModifiedSignal: None
    materialRemovedSignal: None
    entries: hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations


class hkaSkeletonMapperData(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 2

    local_members = (
        Member(0, "skeletonA", Ptr(hkaSkeleton)),
        Member(8, "skeletonB", Ptr(hkaSkeleton)),
        Member(16, "partitionMap", hkArray(hkInt16)),
        Member(32, "simpleMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange)),
        Member(48, "chainMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange)),
        Member(64, "simpleMappings", hkArray(hkaSkeletonMapperDataSimpleMapping)),
        Member(80, "chainMappings", hkArray(hkaSkeletonMapperDataChainMapping)),
        Member(96, "unmappedBones", hkArray(hkInt16)),
        Member(112, "extractedMotionMapping", hkQsTransform),
        Member(160, "keepUnmappedLocal", hkBool),
        Member(164, "mappingType", hkEnum(hkaSkeletonMapperDataMappingType, hkInt32)),
    )
    members = local_members

    skeletonA: hkaSkeleton
    skeletonB: hkaSkeleton
    partitionMap: list[int]
    simpleMappingPartitionRanges: list[hkaSkeletonMapperDataPartitionMappingRange]
    chainMappingPartitionRanges: list[hkaSkeletonMapperDataPartitionMappingRange]
    simpleMappings: list[hkaSkeletonMapperDataSimpleMapping]
    chainMappings: list[hkaSkeletonMapperDataChainMapping]
    unmappedBones: list[int]
    extractedMotionMapping: hkQsTransform
    keepUnmappedLocal: bool
    mappingType: int


class hkxVertexBuffer(hkReferencedObject):
    alignment = 16
    byte_size = 136
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(16, "data", hkxVertexBufferVertexData),
        Member(120, "desc", hkxVertexDescription),
    )
    members = hkReferencedObject.members + local_members

    data: hkxVertexBufferVertexData
    desc: hkxVertexDescription


class hkxMaterial(hkxAttributeHolder):
    alignment = 16
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 5

    local_members = (
        Member(32, "name", hkStringPtr),
        Member(40, "stages", hkArray(hkxMaterialTextureStage)),
        Member(64, "diffuseColor", hkVector4),
        Member(80, "ambientColor", hkVector4),
        Member(96, "specularColor", hkVector4),
        Member(112, "emissiveColor", hkVector4),
        Member(128, "subMaterials", hkArray(Ptr(DefType("hkxMaterial", lambda: hkxMaterial)))),
        Member(144, "extraData", Ptr(hkReferencedObject)),
        Member(152, "uvMapScale", hkStruct(hkReal, 2)),
        Member(160, "uvMapOffset", hkStruct(hkReal, 2)),
        Member(168, "uvMapRotation", hkReal),
        Member(172, "uvMapAlgorithm", hkEnum(hkxMaterialUVMappingAlgorithm, hkUint32)),
        Member(176, "specularMultiplier", hkReal),
        Member(180, "specularExponent", hkReal),
        Member(184, "transparency", hkEnum(hkxMaterialTransparency, hkUint8)),
        Member(192, "userData", hkUlong),
        Member(200, "properties", hkArray(hkxMaterialProperty)),
    )
    members = hkxAttributeHolder.members + local_members

    name: str
    stages: list[hkxMaterialTextureStage]
    diffuseColor: hkVector4
    ambientColor: hkVector4
    specularColor: hkVector4
    emissiveColor: hkVector4
    subMaterials: list[hkxMaterial]
    extraData: hkReferencedObject
    uvMapScale: tuple[float, ...]
    uvMapOffset: tuple[float, ...]
    uvMapRotation: float
    uvMapAlgorithm: int
    specularMultiplier: float
    specularExponent: float
    transparency: int
    userData: int
    properties: list[hkxMaterialProperty]


class hkxVertexAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "time", hkReal),
        Member(24, "vertData", hkxVertexBuffer),
        Member(160, "vertexIndexMap", hkArray(hkInt32)),
        Member(176, "componentMap", hkArray(hkxVertexAnimationUsageMap)),
    )
    members = hkReferencedObject.members + local_members

    time: float
    vertData: hkxVertexBuffer
    vertexIndexMap: list[int]
    componentMap: list[hkxVertexAnimationUsageMap]


class hknpConvexPolytopeShape(hknpConvexShape):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(64, "planes", hkRelArray(hkVector4)),
        Member(68, "faces", hkRelArray(hknpConvexPolytopeShapeFace)),
        Member(72, "indices", hkRelArray(hkUint8)),
    )
    members = hknpConvexShape.members + local_members

    planes: list[hkVector4]
    faces: list[hknpConvexPolytopeShapeFace]
    indices: list[int]


class hkpPositionConstraintMotor(hkpLimitedForceConstraintMotor):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 339596288

    local_members = (
        Member(32, "tau", hkReal),
        Member(36, "damping", hkReal),
        Member(40, "proportionalRecoveryVelocity", hkReal),
        Member(44, "constantRecoveryVelocity", hkReal),
    )
    members = hkpLimitedForceConstraintMotor.members + local_members

    tau: float
    damping: float
    proportionalRecoveryVelocity: float
    constantRecoveryVelocity: float


class hkpRagdollConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 384
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom),
        Member(160, "ragdollMotors", hkpRagdollMotorConstraintAtom),
        Member(256, "angFriction", hkpAngFrictionConstraintAtom),
        Member(272, "twistLimit", hkpTwistLimitConstraintAtom),
        Member(304, "coneLimit", hkpConeLimitConstraintAtom),
        Member(336, "planesLimit", hkpConeLimitConstraintAtom),
        Member(368, "ballSocket", hkpBallSocketConstraintAtom),
    )
    members = local_members

    transforms: hkpSetLocalTransformsConstraintAtom
    setupStabilization: hkpSetupStabilizationAtom
    ragdollMotors: hkpRagdollMotorConstraintAtom
    angFriction: hkpAngFrictionConstraintAtom
    twistLimit: hkpTwistLimitConstraintAtom
    coneLimit: hkpConeLimitConstraintAtom
    planesLimit: hkpConeLimitConstraintAtom
    ballSocket: hkpBallSocketConstraintAtom


class hkpLimitedHingeConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 304
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1374314554

    local_members = (
        Member(32, "atoms", hkpLimitedHingeConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpLimitedHingeConstraintDataAtoms


class hknpRagdollData(hknpPhysicsSystemData):
    alignment = 16
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3700367531

    local_members = (
        Member(120, "skeleton", Ptr(hkaSkeleton)),
        Member(128, "boneToBodyMap", hkArray(hkInt32)),
    )
    members = hknpPhysicsSystemData.members + local_members

    skeleton: hkaSkeleton
    boneToBodyMap: list[int]


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


class hkaSkeletonMapper(hkReferencedObject):
    alignment = 16
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2900984988

    local_members = (
        Member(16, "mapping", hkaSkeletonMapperData),
    )
    members = hkReferencedObject.members + local_members

    mapping: hkaSkeletonMapperData


class hkxMeshSection(hkReferencedObject):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 5

    local_members = (
        Member(16, "vertexBuffer", Ptr(hkxVertexBuffer)),
        Member(24, "indexBuffers", hkArray(Ptr(hkxIndexBuffer))),
        Member(40, "material", Ptr(hkxMaterial)),
        Member(48, "userChannels", hkArray(Ptr(hkReferencedObject))),
        Member(64, "vertexAnimations", hkArray(Ptr(hkxVertexAnimation))),
        Member(80, "linearKeyFrameHints", hkArray(hkReal)),
        Member(96, "boneMatrixMap", hkArray(hkMeshBoneIndexMapping)),
    )
    members = hkReferencedObject.members + local_members

    vertexBuffer: hkxVertexBuffer
    indexBuffers: list[hkxIndexBuffer]
    material: hkxMaterial
    userChannels: list[hkReferencedObject]
    vertexAnimations: list[hkxVertexAnimation]
    linearKeyFrameHints: list[float]
    boneMatrixMap: list[hkMeshBoneIndexMapping]


class hknpCapsuleShape(hknpConvexPolytopeShape):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1621581644

    local_members = (
        Member(80, "a", hkVector4),
        Member(96, "b", hkVector4),
    )
    members = hknpConvexPolytopeShape.members + local_members

    a: hkVector4
    b: hkVector4


class hkpRagdollConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 416
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3078430774

    local_members = (
        Member(32, "atoms", hkpRagdollConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpRagdollConstraintDataAtoms


class hknpRefWorldCinfo(hkReferencedObject):
    alignment = 16
    byte_size = 272
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "info", hknpWorldCinfo),
    )
    members = hkReferencedObject.members + local_members

    info: hknpWorldCinfo


class hkxMesh(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(16, "sections", hkArray(Ptr(hkxMeshSection))),
        Member(32, "userChannelInfos", hkArray(Ptr(hkxMeshUserChannelInfo))),
    )
    members = hkReferencedObject.members + local_members

    sections: list[hkxMeshSection]
    userChannelInfos: list[hkxMeshUserChannelInfo]


class hknpPhysicsSceneData(hkReferencedObject):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1880942380
    __version = 1

    local_members = (
        Member(16, "systemDatas", hkArray(Ptr(hknpPhysicsSystemData))),
        Member(32, "worldCinfo", Ptr(hknpRefWorldCinfo)),
    )
    members = hkReferencedObject.members + local_members

    systemDatas: list[hknpPhysicsSystemData]
    worldCinfo: hknpRefWorldCinfo


class hkaMeshBinding(hkReferencedObject):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(16, "mesh", Ptr(hkxMesh)),
        Member(24, "originalSkeletonName", hkStringPtr),
        Member(32, "name", hkStringPtr),
        Member(40, "skeleton", Ptr(hkaSkeleton)),
        Member(48, "mappings", hkArray(hkaMeshBindingMapping)),
        Member(64, "boneFromSkinMeshTransforms", hkArray(hkTransform)),
    )
    members = hkReferencedObject.members + local_members

    mesh: hkxMesh
    originalSkeletonName: str
    name: str
    skeleton: hkaSkeleton
    mappings: list[hkaMeshBindingMapping]
    boneFromSkinMeshTransforms: list[hkTransform]


class hkaAnimationContainer(hkReferencedObject):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 646291276
    __version = 1

    local_members = (
        Member(16, "skeletons", hkArray(Ptr(hkaSkeleton))),
        Member(32, "animations", hkArray(Ptr(hkaAnimation))),
        Member(48, "bindings", hkArray(Ptr(hkaAnimationBinding))),
        Member(64, "attachments", hkArray(Ptr(hkaBoneAttachment))),
        Member(80, "skins", hkArray(Ptr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]
