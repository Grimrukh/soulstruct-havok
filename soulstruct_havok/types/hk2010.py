"""Auto-generated types for Havok 2010.

Generated from files:
    c2240.hkx
"""
from __future__ import annotations

from soulstruct_havok.enums import TagDataType, MemberFlags
from soulstruct_havok.types.core import *
from soulstruct_havok.types.hk2010_base import *


# --- Invalid Types --- #


# --- Primitive Types --- #


# --- Havok Struct Types --- #


# --- Havok Wrappers --- #


# --- Havok Core Types --- #


class hkaBone(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "lockTranslation", hkBool),
    )
    members = local_members

    name: str
    lockTranslation: bool


class hkLocalFrame(hkReferencedObject):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkaAnimatedReferenceFrame(hkReferencedObject):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkaAnnotationTrackAnnotation(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "time", hkReal),
        Member(4, "text", hkStringPtr),
    )
    members = local_members

    time: float
    text: str


class hkaBoneAttachment(hkReferencedObject):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "originalSkeletonName", hkStringPtr),
        Member(16, "boneFromAttachment", hkMatrix4),
        Member(80, "attachment", Ptr(hkReferencedObject)),
        Member(84, "name", hkStringPtr),
        Member(88, "boneIndex", hkInt16),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    boneFromAttachment: hkMatrix4
    attachment: hkReferencedObject
    name: str
    boneIndex: int


class hkxVertexBufferVertexData(hk):
    alignment = 16
    byte_size = 84
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "vectorData", hkArray(hkVector4)),
        Member(12, "floatData", hkArray(hkReal)),
        Member(24, "uint32Data", hkArray(hkUint32)),
        Member(36, "uint16Data", hkArray(hkUint16)),
        Member(48, "uint8Data", hkArray(hkUint8)),
        Member(60, "numVerts", hkUint32),
        Member(64, "vectorStride", hkUint32),
        Member(68, "floatStride", hkUint32),
        Member(72, "uint32Stride", hkUint32),
        Member(76, "uint16Stride", hkUint32),
        Member(80, "uint8Stride", hkUint32),
    )
    members = local_members

    vectorData: list[hkVector4]
    floatData: list[float]
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
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "value", Ptr(hkReferencedObject)),
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


class hkaMeshBindingMapping(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "mapping", hkArray(hkInt16)),
    )
    members = local_members

    mapping: list[int]


class hkpBroadPhaseHandle(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "id", hkUint32, MemberFlags.NotSerializable),
    )
    members = local_members

    id: int


class hkpCollidableBoundingVolumeData(hk):
    alignment = 16
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "min", hkStruct(hkUint32, 3)),
        Member(12, "expansionMin", hkStruct(hkUint8, 3)),
        Member(15, "expansionShift", hkUint8),
        Member(16, "max", hkStruct(hkUint32, 3)),
        Member(28, "expansionMax", hkStruct(hkUint8, 3)),
        Member(31, "padding", hkUint8),
        Member(32, "numChildShapeAabbs", hkUint16, MemberFlags.NotSerializable),
        Member(34, "capacityChildShapeAabbs", hkUint16, MemberFlags.NotSerializable),
        Member(36, "childShapeAabbs", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(40, "childShapeKeys", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = local_members

    min: tuple[int, ...]
    expansionMin: tuple[int, ...]
    expansionShift: int
    max: tuple[int, ...]
    expansionMax: tuple[int, ...]
    padding: int
    numChildShapeAabbs: int
    capacityChildShapeAabbs: int
    childShapeAabbs: None
    childShapeKeys: None


class hkMultiThreadCheck(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "threadId", hkUint32, MemberFlags.NotSerializable),
        Member(4, "stackTraceId", hkInt32, MemberFlags.NotSerializable),
        Member(8, "markCount", hkUint16, MemberFlags.NotSerializable),
        Member(10, "markBitStack", hkUint16, MemberFlags.NotSerializable),
    )
    members = local_members

    threadId: int
    stackTraceId: int
    markCount: int
    markBitStack: int


class hkpPropertyValue(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "data", hkUint64),
    )
    members = local_members

    data: int


class hkpEntitySmallArraySerializeOverrideType(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "data", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(4, "size", hkUint16),
        Member(6, "capacityAndFlags", hkUint16),
    )
    members = local_members

    data: None
    size: int
    capacityAndFlags: int


class hkpConstraintData(hkReferencedObject):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "userData", hkUlong),
    )
    members = hkReferencedObject.members + local_members

    userData: int


class hkpConstraintInstanceSmallArraySerializeOverrideType(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "data", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(4, "size", hkUint16),
        Member(6, "capacityAndFlags", hkUint16),
    )
    members = local_members

    data: None
    size: int
    capacityAndFlags: int


class hkpEntitySpuCollisionCallback(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "util", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(4, "capacity", hkUint16, MemberFlags.NotSerializable),
        Member(6, "eventFilter", hkUint8),
        Member(7, "userFilter", hkUint8),
    )
    members = local_members

    util: None
    capacity: int
    eventFilter: int
    userFilter: int


class hkSweptTransform(hk):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "centerOfMass0", hkVector4),
        Member(16, "centerOfMass1", hkVector4),
        Member(32, "rotation0", hkQuaternionf),
        Member(48, "rotation1", hkQuaternionf),
        Member(64, "centerOfMassLocal", hkVector4),
    )
    members = local_members

    centerOfMass0: hkVector4
    centerOfMass1: hkVector4
    rotation0: hkQuaternionf
    rotation1: hkQuaternionf
    centerOfMassLocal: hkVector4


class hkpEntityExtendedListeners(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "activationListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(8, "entityListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
    )
    members = local_members

    activationListeners: hkpEntitySmallArraySerializeOverrideType
    entityListeners: hkpEntitySmallArraySerializeOverrideType


class hkpAction(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "world", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(12, "island", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(16, "userData", hkUlong),
        Member(20, "name", hkStringPtr),
    )
    members = hkReferencedObject.members + local_members

    world: None
    island: None
    userData: int
    name: str


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


class hkpConvexListFilter(hkReferencedObject):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkWorldMemoryAvailableWatchDog(hkReferencedObject):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


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
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "className", hkStringPtr),
        Member(8, "variant", Ptr(hkReferencedObject)),
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


class hkxMaterialTextureStageTextureType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32
    __real_name = "hkxMaterialTextureStage::TextureType"
    local_members = ()


class hkpShapeShapeType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.Int32
    __real_name = "hkpShape::ShapeType"
    local_members = ()


class hkpMaterialResponseType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkpMaterial::ResponseType"
    local_members = ()


class hkpConstraintInstanceConstraintPriority(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hkpConstraintInstance::ConstraintPriority"
    local_members = ()


class hkpConstraintInstanceOnDestructionRemapInfo(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hkpConstraintInstance::OnDestructionRemapInfo"
    local_members = ()


class hkpConstraintAtomAtomType(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16
    __real_name = "hkpConstraintAtom::AtomType"
    local_members = ()


class hkpMotionMotionType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8
    __real_name = "hkpMotion::MotionType"
    local_members = ()


class hkpConstraintMotorMotorType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkpConstraintMotor::MotorType"
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


class hkpWorldCinfoBroadPhaseBorderBehaviour(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkpWorldCinfo::BroadPhaseBorderBehaviour"
    local_members = ()


class hkpWorldCinfoTreeUpdateType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkpWorldCinfo::TreeUpdateType"
    local_members = ()


class hkpWorldCinfoContactPointGeneration(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkpWorldCinfo::ContactPointGeneration"
    local_members = ()


class hkpWorldCinfoSimulationType(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkpWorldCinfo::SimulationType"
    local_members = ()


class hkpCollisionFilterhkpFilterType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.Int32
    __real_name = "hkpCollisionFilter::hkpFilterType"
    local_members = ()


class hkaSkeletonMapperDataMappingType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32
    __real_name = "hkaSkeletonMapperData::MappingType"
    local_members = ()


class hkaSkeletonLocalFrameOnBone(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "localFrame", Ptr(hkLocalFrame)),
        Member(4, "boneIndex", hkInt32),
    )
    members = local_members

    localFrame: hkLocalFrame
    boneIndex: int


class hkaAnnotationTrack(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "trackName", hkStringPtr),
        Member(4, "annotations", hkArray(hkaAnnotationTrackAnnotation)),
    )
    members = local_members

    trackName: str
    annotations: list[hkaAnnotationTrackAnnotation]


class hkxVertexDescriptionElementDecl(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "byteOffset", hkUint32),
        Member(4, "type", hkEnum(hkxVertexDescriptionElementDeclDataType, hkUint16)),
        Member(6, "usage", hkEnum(hkxVertexDescriptionElementDeclDataUsage, hkUint16)),
        Member(8, "byteStride", hkUint32),
        Member(12, "numElements", hkUint8),
    )
    members = local_members

    byteOffset: int
    type: int
    usage: int
    byteStride: int
    numElements: int


class hkxIndexBuffer(hkReferencedObject):
    alignment = 16
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "indexType", hkEnum(hkxIndexBufferIndexType, hkInt8)),
        Member(12, "indices16", hkArray(hkUint16)),
        Member(24, "indices32", hkArray(hkUint32)),
        Member(36, "vertexBaseOffset", hkUint32),
        Member(40, "length", hkUint32),
    )
    members = hkReferencedObject.members + local_members

    indexType: int
    indices16: list[int]
    indices32: list[int]
    vertexBaseOffset: int
    length: int


class hkxAttributeGroup(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(4, "attributes", hkArray(hkxAttribute)),
    )
    members = local_members

    name: str
    attributes: list[hkxAttribute]


class hkxMaterialTextureStage(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "texture", Ptr(hkReferencedObject)),
        Member(4, "usageHint", hkEnum(hkxMaterialTextureStageTextureType, hkInt32)),
        Member(8, "tcoordChannel", hkInt32),
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: int
    tcoordChannel: int


class hkpShape(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "userData", hkUlong),
        Member(12, "type", hkEnum(hkpShapeShapeType, hkUint32), MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    userData: int
    type: int


class hkpCdBody(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "shape", Ptr(hkpShape)),
        Member(4, "shapeKey", hkUint32),
        Member(8, "motion", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(12, "parent", Ptr(DefType("hkpCdBody", lambda: hkpCdBody)), MemberFlags.NotSerializable),
    )
    members = local_members

    shape: hkpShape
    shapeKey: int
    motion: None
    parent: hkpCdBody


class hkpTypedBroadPhaseHandle(hkpBroadPhaseHandle):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(4, "type", hkInt8),
        Member(5, "ownerOffset", hkInt8, MemberFlags.NotSerializable),
        Member(6, "objectQualityType", hkInt8),
        Member(8, "collisionFilterInfo", hkUint32),
    )
    members = hkpBroadPhaseHandle.members + local_members

    type: int
    ownerOffset: int
    objectQualityType: int
    collisionFilterInfo: int


class hkpProperty(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "key", hkUint32),
        Member(4, "alignmentPadding", hkUint32),
        Member(8, "value", hkpPropertyValue),
    )
    members = local_members

    key: int
    alignmentPadding: int
    value: hkpPropertyValue


class hkpMaterial(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "responseType", hkEnum(hkpMaterialResponseType, hkInt8)),
        Member(2, "rollingFrictionMultiplier", hkHalf16),
        Member(4, "friction", hkReal),
        Member(8, "restitution", hkReal),
    )
    members = local_members

    responseType: int
    rollingFrictionMultiplier: hkHalf16
    friction: float
    restitution: float


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


class hkMotionState(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "transform", hkTransform),
        Member(64, "sweptTransform", hkSweptTransform),
        Member(144, "deltaAngle", hkVector4),
        Member(160, "objectRadius", hkReal),
        Member(164, "linearDamping", hkHalf16),
        Member(166, "angularDamping", hkHalf16),
        Member(168, "timeFactor", hkHalf16),
        Member(170, "maxLinearVelocity", hkUint8),
        Member(171, "maxAngularVelocity", hkUint8),
        Member(172, "deactivationClass", hkUint8),
    )
    members = local_members

    transform: hkTransform
    sweptTransform: hkSweptTransform
    deltaAngle: hkVector4
    objectRadius: float
    linearDamping: hkHalf16
    angularDamping: hkHalf16
    timeFactor: hkHalf16
    maxLinearVelocity: int
    maxAngularVelocity: int
    deactivationClass: int


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


class hkpSetupStabilizationAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "enabled", hkBool),
        Member(4, "maxAngle", hkReal),
        Member(8, "padding", hkStruct(hkUint8, 8)),
    )
    members = hkpConstraintAtom.members + local_members

    enabled: bool
    maxAngle: float
    padding: tuple[int, ...]


class hkpConstraintMotor(hkReferencedObject):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "type", hkEnum(hkpConstraintMotorMotorType, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    type: int


class hkpAngFrictionConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "firstFrictionAxis", hkUint8),
        Member(4, "numFrictionAxes", hkUint8),
        Member(8, "maxFrictionTorque", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    firstFrictionAxis: int
    numFrictionAxes: int
    maxFrictionTorque: float


class hkpTwistLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "twistAxis", hkUint8),
        Member(4, "refAxis", hkUint8),
        Member(8, "minAngle", hkReal),
        Member(12, "maxAngle", hkReal),
        Member(16, "angularLimitsTauFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    twistAxis: int
    refAxis: int
    minAngle: float
    maxAngle: float
    angularLimitsTauFactor: float


class hkpConeLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 20
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


class hkpBallSocketConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "solvingMethod", hkEnum(hkpBallSocketConstraintAtomSolvingMethod, hkUint8)),
        Member(3, "bodiesToNotify", hkUint8),
        Member(4, "velocityStabilizationFactor", hkUint8),
        Member(8, "maxImpulse", hkReal),
        Member(12, "inertiaStabilizationFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    solvingMethod: int
    bodiesToNotify: int
    velocityStabilizationFactor: int
    maxImpulse: float
    inertiaStabilizationFactor: float


class hkpCollisionFilter(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(24, "prepad", hkStruct(hkUint32, 2)),
        Member(32, "type", hkEnum(hkpCollisionFilterhkpFilterType, hkUint32)),
        Member(36, "postpad", hkStruct(hkUint32, 3)),
    )
    members = hkReferencedObject.members + local_members

    prepad: tuple[int, ...]
    type: int
    postpad: tuple[int, ...]


class hkpLimitedForceConstraintMotor(hkpConstraintMotor):
    alignment = 16
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(12, "minForce", hkReal),
        Member(16, "maxForce", hkReal),
    )
    members = hkpConstraintMotor.members + local_members

    minForce: float
    maxForce: float


class hkRootLevelContainer(hk):
    alignment = 16
    byte_size = 12
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
    byte_size = 84
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 913211936

    local_members = (
        Member(8, "name", hkStringPtr),
        Member(12, "parentIndices", hkArray(hkInt16)),
        Member(24, "bones", hkArray(hkaBone)),
        Member(36, "referencePose", hkArray(hkQsTransform)),
        Member(48, "referenceFloats", hkArray(hkReal)),
        Member(60, "floatSlots", hkArray(hkStringPtr)),
        Member(72, "localFrames", hkArray(hkaSkeletonLocalFrameOnBone)),
    )
    members = hkReferencedObject.members + local_members

    name: str
    parentIndices: list[int]
    bones: list[hkaBone]
    referencePose: list[hkQsTransform]
    referenceFloats: list[float]
    floatSlots: list[str]
    localFrames: list[hkaSkeletonLocalFrameOnBone]


class hkaAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "type", hkEnum(hkaAnimationAnimationType, hkInt32)),
        Member(12, "duration", hkReal),
        Member(16, "numberOfTransformTracks", hkInt32),
        Member(20, "numberOfFloatTracks", hkInt32),
        Member(24, "extractedMotion", Ptr(hkaAnimatedReferenceFrame)),
        Member(28, "annotationTracks", hkArray(hkaAnnotationTrack)),
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
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "originalSkeletonName", hkStringPtr),
        Member(12, "animation", Ptr(hkaAnimation)),
        Member(16, "transformTrackToBoneIndices", hkArray(hkInt16)),
        Member(28, "floatTrackToFloatSlotIndices", hkArray(hkInt16)),
        Member(40, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    animation: hkaAnimation
    transformTrackToBoneIndices: list[int]
    floatTrackToFloatSlotIndices: list[int]
    blendHint: int


class hkxVertexDescription(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "decls", hkArray(hkxVertexDescriptionElementDecl)),
    )
    members = local_members

    decls: list[hkxVertexDescriptionElementDecl]


class hkxAttributeHolder(hkReferencedObject):
    alignment = 16
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "attributeGroups", hkArray(hkxAttributeGroup)),
    )
    members = hkReferencedObject.members + local_members

    attributeGroups: list[hkxAttributeGroup]


class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 16
    byte_size = 28
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(20, "name", hkStringPtr),
        Member(24, "className", hkStringPtr),
    )
    members = hkxAttributeHolder.members + local_members

    name: str
    className: str


class hkpSphereRepShape(hkpShape):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkpCollidable(hkpCdBody):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "ownerOffset", hkInt8, MemberFlags.NotSerializable),
        Member(17, "forceCollideOntoPpu", hkUint8),
        Member(18, "shapeSizeOnSpu", hkUint16, MemberFlags.NotSerializable),
        Member(20, "broadPhaseHandle", hkpTypedBroadPhaseHandle),
        Member(32, "boundingVolumeData", hkpCollidableBoundingVolumeData, MemberFlags.NotSerializable),
        Member(76, "allowedPenetrationDepth", hkReal),
    )
    members = hkpCdBody.members + local_members

    ownerOffset: int
    forceCollideOntoPpu: int
    shapeSizeOnSpu: int
    broadPhaseHandle: hkpTypedBroadPhaseHandle
    boundingVolumeData: hkpCollidableBoundingVolumeData
    allowedPenetrationDepth: float


class hkpModifierConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "modifierAtomSize", hkUint16),
        Member(18, "childSize", hkUint16),
        Member(20, "child", Ptr(hkpConstraintAtom)),
        Member(24, "pad", hkStruct(hkUint32, 2)),
    )
    members = hkpConstraintAtom.members + local_members

    modifierAtomSize: int
    childSize: int
    child: hkpConstraintAtom
    pad: tuple[int, ...]


class hkpMotion(hkReferencedObject):
    alignment = 16
    byte_size = 288
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "type", hkEnum(hkpMotionMotionType, hkUint8)),
        Member(9, "deactivationIntegrateCounter", hkUint8),
        Member(10, "deactivationNumInactiveFrames", hkStruct(hkUint16, 2)),
        Member(16, "motionState", hkMotionState),
        Member(192, "inertiaAndMassInv", hkVector4),
        Member(208, "linearVelocity", hkVector4),
        Member(224, "angularVelocity", hkVector4),
        Member(240, "deactivationRefPosition", hkStruct(hkVector4, 2)),
        Member(272, "deactivationRefOrientation", hkStruct(hkUint32, 2)),
        Member(280, "savedMotion", Ptr(DefType("hkpMaxSizeMotion", lambda: hkpMaxSizeMotion))),
        Member(284, "savedQualityTypeIndex", hkUint16),
        Member(286, "gravityFactor", hkHalf16),
    )
    members = hkReferencedObject.members + local_members

    type: int
    deactivationIntegrateCounter: int
    deactivationNumInactiveFrames: tuple[int, ...]
    motionState: hkMotionState
    inertiaAndMassInv: hkVector4
    linearVelocity: hkVector4
    angularVelocity: hkVector4
    deactivationRefPosition: tuple[hkVector4, ...]
    deactivationRefOrientation: tuple[int, ...]
    savedMotion: hkpMaxSizeMotion
    savedQualityTypeIndex: int
    gravityFactor: hkHalf16


class hkpRagdollMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "isEnabled", hkBool),
        Member(4, "initializedOffset", hkInt16),
        Member(6, "previousTargetAnglesOffset", hkInt16),
        Member(16, "target_bRca", hkMatrix3),
        Member(64, "motors", hkStruct(Ptr(hkpConstraintMotor), 3)),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: bool
    initializedOffset: int
    previousTargetAnglesOffset: int
    target_bRca: hkMatrix3
    motors: tuple[hkpConstraintMotor, ...]


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

    gravity: hkVector4
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


class hkpPositionConstraintMotor(hkpLimitedForceConstraintMotor):
    alignment = 16
    byte_size = 36
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1955574531

    local_members = (
        Member(20, "tau", hkReal),
        Member(24, "damping", hkReal),
        Member(28, "proportionalRecoveryVelocity", hkReal),
        Member(32, "constantRecoveryVelocity", hkReal),
    )
    members = hkpLimitedForceConstraintMotor.members + local_members

    tau: float
    damping: float
    proportionalRecoveryVelocity: float
    constantRecoveryVelocity: float


class hkaSkeletonMapperData(hk):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "skeletonA", Ptr(hkaSkeleton)),
        Member(4, "skeletonB", Ptr(hkaSkeleton)),
        Member(8, "simpleMappings", hkArray(hkaSkeletonMapperDataSimpleMapping)),
        Member(20, "chainMappings", hkArray(hkaSkeletonMapperDataChainMapping)),
        Member(32, "unmappedBones", hkArray(hkInt16)),
        Member(48, "extractedMotionMapping", hkQsTransform),
        Member(96, "keepUnmappedLocal", hkBool),
        Member(100, "mappingType", hkEnum(hkaSkeletonMapperDataMappingType, hkInt32)),
    )
    members = local_members

    skeletonA: hkaSkeleton
    skeletonB: hkaSkeleton
    simpleMappings: list[hkaSkeletonMapperDataSimpleMapping]
    chainMappings: list[hkaSkeletonMapperDataChainMapping]
    unmappedBones: list[int]
    extractedMotionMapping: hkQsTransform
    keepUnmappedLocal: bool
    mappingType: int


class hkxVertexBuffer(hkReferencedObject):
    alignment = 16
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "data", hkxVertexBufferVertexData),
        Member(92, "desc", hkxVertexDescription),
    )
    members = hkReferencedObject.members + local_members

    data: hkxVertexBufferVertexData
    desc: hkxVertexDescription


class hkxMaterial(hkxAttributeHolder):
    alignment = 16
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(20, "name", hkStringPtr),
        Member(24, "stages", hkArray(hkxMaterialTextureStage)),
        Member(48, "diffuseColor", hkVector4),
        Member(64, "ambientColor", hkVector4),
        Member(80, "specularColor", hkVector4),
        Member(96, "emissiveColor", hkVector4),
        Member(112, "subMaterials", hkArray(Ptr(DefType("hkxMaterial", lambda: hkxMaterial)))),
        Member(124, "extraData", Ptr(hkReferencedObject)),
        Member(128, "properties", hkArray(hkxMaterialProperty)),
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
    properties: list[hkxMaterialProperty]


class hkpConvexShape(hkpSphereRepShape):
    alignment = 16
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "radius", hkReal),
    )
    members = hkpSphereRepShape.members + local_members

    radius: float


class hkpLinkedCollidable(hkpCollidable):
    alignment = 16
    byte_size = 92
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(80, "collisionEntries", hkArray(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = hkpCollidable.members + local_members

    collisionEntries: list


class hkpKeyframedRigidMotion(hkpMotion):
    alignment = 16
    byte_size = 288
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkpRagdollConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 336
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom),
        Member(160, "ragdollMotors", hkpRagdollMotorConstraintAtom),
        Member(240, "angFriction", hkpAngFrictionConstraintAtom),
        Member(252, "twistLimit", hkpTwistLimitConstraintAtom),
        Member(272, "coneLimit", hkpConeLimitConstraintAtom),
        Member(292, "planesLimit", hkpConeLimitConstraintAtom),
        Member(312, "ballSocket", hkpBallSocketConstraintAtom),
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


class hkaSkeletonMapper(hkReferencedObject):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 316621477

    local_members = (
        Member(16, "mapping", hkaSkeletonMapperData),
    )
    members = hkReferencedObject.members + local_members

    mapping: hkaSkeletonMapperData


class hkxMeshSection(hkReferencedObject):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "vertexBuffer", Ptr(hkxVertexBuffer)),
        Member(12, "indexBuffers", hkArray(Ptr(hkxIndexBuffer))),
        Member(24, "material", Ptr(hkxMaterial)),
        Member(28, "userChannels", hkArray(Ptr(hkReferencedObject))),
    )
    members = hkReferencedObject.members + local_members

    vertexBuffer: hkxVertexBuffer
    indexBuffers: list[hkxIndexBuffer]
    material: hkxMaterial
    userChannels: list[hkReferencedObject]


class hkpCapsuleShape(hkpConvexShape):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3708493779

    local_members = (
        Member(32, "vertexA", hkVector4),
        Member(48, "vertexB", hkVector4),
    )
    members = hkpConvexShape.members + local_members

    vertexA: hkVector4
    vertexB: hkVector4


class hkpWorldObject(hkReferencedObject):
    alignment = 16
    byte_size = 140
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "world", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(12, "userData", hkUlong),
        Member(16, "collidable", hkpLinkedCollidable),
        Member(108, "multiThreadCheck", hkMultiThreadCheck),
        Member(120, "name", hkStringPtr),
        Member(124, "properties", hkArray(hkpProperty)),
        Member(136, "treeData", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    world: None
    userData: int
    collidable: hkpLinkedCollidable
    multiThreadCheck: hkMultiThreadCheck
    name: str
    properties: list[hkpProperty]
    treeData: None


class hkpMaxSizeMotion(hkpKeyframedRigidMotion):
    alignment = 16
    byte_size = 288
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkpRagdollConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 352
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2411060521

    local_members = (
        Member(16, "atoms", hkpRagdollConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpRagdollConstraintDataAtoms


class hkpPhantom(hkpWorldObject):
    alignment = 16
    byte_size = 164
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(140, "overlapListeners", hkArray(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(152, "phantomListeners", hkArray(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = hkpWorldObject.members + local_members

    overlapListeners: list
    phantomListeners: list


class hkxMesh(hkReferencedObject):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "sections", hkArray(Ptr(hkxMeshSection))),
        Member(20, "userChannelInfos", hkArray(Ptr(hkxMeshUserChannelInfo))),
    )
    members = hkReferencedObject.members + local_members

    sections: list[hkxMeshSection]
    userChannelInfos: list[hkxMeshUserChannelInfo]


class hkpEntity(hkpWorldObject):
    alignment = 16
    byte_size = 544
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(140, "material", hkpMaterial),
        Member(152, "limitContactImpulseUtilAndFlag", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(156, "damageMultiplier", hkReal),
        Member(160, "breakableBody", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(164, "solverData", hkUint32, MemberFlags.NotSerializable),
        Member(168, "storageIndex", hkUint16),
        Member(170, "contactPointCallbackDelay", hkUint16),
        Member(172, "constraintsMaster", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(
            180,
            "constraintsSlave",
            hkArray(Ptr(hkViewPtr("hkpConstraintInstance"))),
            MemberFlags.NotSerializable,
        ),
        Member(192, "constraintRuntime", hkArray(hkUint8), MemberFlags.NotSerializable),
        Member(204, "simulationIsland", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(208, "autoRemoveLevel", hkInt8),
        Member(209, "numShapeKeysInContactPointProperties", hkUint8),
        Member(210, "responseModifierFlags", hkUint8),
        Member(212, "uid", hkUint32),
        Member(216, "spuCollisionCallback", hkpEntitySpuCollisionCallback),
        Member(224, "motion", hkpMaxSizeMotion),
        Member(512, "contactListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(520, "actions", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(528, "localFrame", Ptr(hkLocalFrame)),
        Member(532, "extendedListeners", Ptr(hkpEntityExtendedListeners), MemberFlags.NotSerializable),
        Member(536, "npData", hkUint32),
    )
    members = hkpWorldObject.members + local_members

    material: hkpMaterial
    limitContactImpulseUtilAndFlag: None
    damageMultiplier: float
    breakableBody: None
    solverData: int
    storageIndex: int
    contactPointCallbackDelay: int
    constraintsMaster: hkpEntitySmallArraySerializeOverrideType
    constraintsSlave: list[hkpConstraintInstance]
    constraintRuntime: list[int]
    simulationIsland: None
    autoRemoveLevel: int
    numShapeKeysInContactPointProperties: int
    responseModifierFlags: int
    uid: int
    spuCollisionCallback: hkpEntitySpuCollisionCallback
    motion: hkpMaxSizeMotion
    contactListeners: hkpEntitySmallArraySerializeOverrideType
    actions: hkpEntitySmallArraySerializeOverrideType
    localFrame: hkLocalFrame
    extendedListeners: hkpEntityExtendedListeners
    npData: int


class hkpConstraintInstance(hkReferencedObject):
    alignment = 16
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 55491167

    local_members = (
        Member(8, "owner", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(12, "data", Ptr(hkpConstraintData)),
        Member(16, "constraintModifiers", Ptr(hkpModifierConstraintAtom)),
        Member(20, "entities", hkStruct(Ptr(hkpEntity), 2)),
        Member(28, "priority", hkEnum(hkpConstraintInstanceConstraintPriority, hkUint8)),
        Member(29, "wantRuntime", hkBool),
        Member(30, "destructionRemapInfo", hkEnum(hkpConstraintInstanceOnDestructionRemapInfo, hkUint8)),
        Member(
            32,
            "listeners",
            hkpConstraintInstanceSmallArraySerializeOverrideType,
            MemberFlags.NotSerializable,
        ),
        Member(40, "name", hkStringPtr),
        Member(44, "userData", hkUlong),
        Member(48, "internal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(52, "uid", hkUint32, MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    owner: None
    data: hkpConstraintData
    constraintModifiers: hkpModifierConstraintAtom
    entities: tuple[hkpEntity, ...]
    priority: int
    wantRuntime: bool
    destructionRemapInfo: int
    listeners: hkpConstraintInstanceSmallArraySerializeOverrideType
    name: str
    userData: int
    internal: None
    uid: int


class hkaMeshBinding(hkReferencedObject):
    alignment = 16
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "mesh", Ptr(hkxMesh)),
        Member(12, "originalSkeletonName", hkStringPtr),
        Member(16, "skeleton", Ptr(hkaSkeleton)),
        Member(20, "mappings", hkArray(hkaMeshBindingMapping)),
        Member(32, "boneFromSkinMeshTransforms", hkArray(hkTransform)),
    )
    members = hkReferencedObject.members + local_members

    mesh: hkxMesh
    originalSkeletonName: str
    skeleton: hkaSkeleton
    mappings: list[hkaMeshBindingMapping]
    boneFromSkinMeshTransforms: list[hkTransform]


class hkpRigidBody(hkpEntity):
    alignment = 16
    byte_size = 544
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1979242501
    local_members = ()


class hkpPhysicsSystem(hkReferencedObject):
    alignment = 16
    byte_size = 68
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4285680663

    local_members = (
        Member(8, "rigidBodies", hkArray(Ptr(hkpRigidBody))),
        Member(20, "constraints", hkArray(Ptr(hkpConstraintInstance))),
        Member(32, "actions", hkArray(Ptr(hkpAction))),
        Member(44, "phantoms", hkArray(Ptr(hkpPhantom))),
        Member(56, "name", hkStringPtr),
        Member(60, "userData", hkUlong),
        Member(64, "active", hkBool),
    )
    members = hkReferencedObject.members + local_members

    rigidBodies: list[hkpRigidBody]
    constraints: list[hkpConstraintInstance]
    actions: list[hkpAction]
    phantoms: list[hkpPhantom]
    name: str
    userData: int
    active: bool


class hkpPhysicsData(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3265552868

    local_members = (
        Member(8, "worldCinfo", Ptr(hkpWorldCinfo)),
        Member(12, "systems", hkArray(Ptr(hkpPhysicsSystem))),
    )
    members = hkReferencedObject.members + local_members

    worldCinfo: hkpWorldCinfo
    systems: list[hkpPhysicsSystem]


class hkaRagdollInstance(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 357124328

    local_members = (
        Member(8, "rigidBodies", hkArray(Ptr(hkpRigidBody))),
        Member(20, "constraints", hkArray(Ptr(hkpConstraintInstance))),
        Member(32, "boneToRigidBodyMap", hkArray(hkInt32)),
        Member(44, "skeleton", Ptr(hkaSkeleton)),
    )
    members = hkReferencedObject.members + local_members

    rigidBodies: list[hkpRigidBody]
    constraints: list[hkpConstraintInstance]
    boneToRigidBodyMap: list[int]
    skeleton: hkaSkeleton


class hkaAnimationContainer(hkReferencedObject):
    alignment = 16
    byte_size = 68
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2378302259

    local_members = (
        Member(8, "skeletons", hkArray(Ptr(hkaSkeleton))),
        Member(20, "animations", hkArray(Ptr(hkaAnimation))),
        Member(32, "bindings", hkArray(Ptr(hkaAnimationBinding))),
        Member(44, "attachments", hkArray(Ptr(hkaBoneAttachment))),
        Member(56, "skins", hkArray(Ptr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]
