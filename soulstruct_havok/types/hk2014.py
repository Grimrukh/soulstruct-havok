"""Auto-generated types for Havok 2014."""
from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import TagDataType, MemberFlags


# --- Invalid Types --- #


class hkReflectDetailOpaque(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 1
    __real_name = "hkReflect::Detail::Opaque"
    local_members = ()


# --- Primitive Types --- #


class _int(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 33284

    __hsh = 4062341138
    __real_name = "int"
    local_members = ()


class _const_char(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 3
    __real_name = "const char*"
    local_members = ()


class _unsigned_short(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "unsigned short"
    local_members = ()


class _char(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196

    __hsh = 4184862313
    __real_name = "char"
    local_members = ()


class _float(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 1525253
    __real_name = "float"
    local_members = ()


class _short(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 9
    tag_type_flags = 16900
    __real_name = "short"
    local_members = ()


class _signed_char(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8708
    __real_name = "signed char"
    local_members = ()


class _unsigned_long_long(hk):
    alignment = 8
    byte_size = 8
    tag_format_flags = 9
    tag_type_flags = 65540
    __real_name = "unsigned long long"
    local_members = ()


class _unsigned_int(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 32772
    __real_name = "unsigned int"
    local_members = ()


class _unsigned_char(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "unsigned char"
    local_members = ()


class _void(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 25
    tag_type_flags = 0

    __abstract_value = 1
    __real_name = "void"
    local_members = ()


# --- Havok Struct Types --- #


class hkVector4f(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_format_flags = 11
    tag_type_flags = 1064
    local_members = ()


class hkQuaternionf(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_format_flags = 43
    tag_type_flags = 1064

    local_members = (
        Member(0, "vec", hkVector4f),
    )
    members = local_members

    vec: hkVector4f


class hkRotationImpl(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 48
    tag_format_flags = 11
    tag_type_flags = 3112
    local_members = ()

    __templates = (
        TemplateType("tFT", type=_float),
    )


class hkVector4(hkVector4f):
    """Havok alias."""
    local_members = ()


class hkMatrix3Impl(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 48
    tag_format_flags = 11
    tag_type_flags = 3112
    local_members = ()

    __templates = (
        TemplateType("tFT", type=_float),
    )


class hkMatrix4f(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    tag_format_flags = 43
    tag_type_flags = 4136

    local_members = (
        Member(0, "col0", hkVector4f, MemberFlags.Protected),
        Member(16, "col1", hkVector4f, MemberFlags.Protected),
        Member(32, "col2", hkVector4f, MemberFlags.Protected),
        Member(48, "col3", hkVector4f, MemberFlags.Protected),
    )
    members = local_members

    col0: hkVector4f
    col1: hkVector4f
    col2: hkVector4f
    col3: hkVector4f


class hkRotationf(hkRotationImpl):
    """Havok alias."""
    local_members = ()


class hkMatrix3f(hkMatrix3Impl):
    """Havok alias."""
    local_members = ()


class hkMatrix4(hkMatrix4f):
    """Havok alias."""
    local_members = ()


class hkTransformf(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    tag_format_flags = 43
    tag_type_flags = 4136

    local_members = (
        Member(0, "rotation", hkRotationf, MemberFlags.Protected),
        Member(48, "translation", hkVector4f, MemberFlags.Protected),
    )
    members = local_members

    rotation: hkRotationf
    translation: hkVector4f


class hkMatrix3(hkMatrix3f):
    """Havok alias."""
    local_members = ()


class hkTransform(hkTransformf):
    """Havok alias."""
    local_members = ()


class hkQsTransformf(hk):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "translation", hkVector4f),
        Member(16, "rotation", hkQuaternionf),
        Member(32, "scale", hkVector4f),
    )
    members = local_members

    translation: hkVector4f
    rotation: hkQuaternionf
    scale: hkVector4f


class hkQsTransform(hkQsTransformf):
    """Havok alias."""
    __hsh = 3766916239
    local_members = ()


# --- Havok Wrappers --- #


class hkUint16(_unsigned_short):
    """Havok alias."""
    local_members = ()


class hkReal(_float):
    """Havok alias."""
    local_members = ()


class hkInt16(_short):
    """Havok alias."""
    __hsh = 1556469994
    local_members = ()


class hkInt32(_int):
    """Havok alias."""
    local_members = ()


class hkInt8(_signed_char):
    """Havok alias."""
    local_members = ()


class hkUlong(_unsigned_long_long):
    """Havok alias."""
    local_members = ()


class hkUint32(_unsigned_int):
    """Havok alias."""
    local_members = ()


class hkUint8(_unsigned_char):
    """Havok alias."""
    local_members = ()


class hkUint64(_unsigned_long_long):
    """Havok alias."""
    local_members = ()


class hkUintReal(_unsigned_int):
    """Havok alias."""
    local_members = ()


# --- Havok Core Types --- #


class hkBaseObject(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkReferencedObject(hkBaseObject):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "memSizeAndRefCount", hkUint32, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkBaseObject.members + local_members

    memSizeAndRefCount: int


class hkRefVariant(hk):
    alignment = 8
    byte_size = 8
    tag_format_flags = 43
    tag_type_flags = 6

    __hsh = 2872857893

    local_members = (
        Member(0, "ptr", Ptr(hkReferencedObject), MemberFlags.Private),
    )
    members = local_members

    ptr: hkReferencedObject


class hkLocalFrame(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkaAnimatedReferenceFrame(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "frameType", hkInt8, MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    frameType: int


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
        Member(0, "centerOfMass", hkGenericStruct(hkInt16, 4)),
        Member(8, "inertia", hkGenericStruct(hkInt16, 4)),
        Member(16, "majorAxisSpace", hkGenericStruct(hkInt16, 4)),
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


class hkUFloat8(hk):
    alignment = 2
    byte_size = 1
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "value", hkUint8),
    )
    members = local_members

    value: int


class hknpSurfaceVelocity(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


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


class hkContainerHeapAllocator(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 57
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __abstract_value = 16
    local_members = ()


class hkStringPtr(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 3

    __hsh = 2837000324

    local_members = (
        Member(0, "stringAndFlag", _const_char, MemberFlags.Private),
    )
    members = local_members

    stringAndFlag: _const_char


class hkBool(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 8194

    local_members = (
        Member(0, "bool", _char, MemberFlags.Private),
    )
    members = local_members

    bool: _char


class hkHalf16(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = 476677

    local_members = (
        Member(0, "value", hkInt16, MemberFlags.Private),
    )
    members = local_members

    value: int


class hkaAnimationAnimationType(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 33284
    __real_name = "hkaAnimation::AnimationType"
    local_members = ()


class hkaAnimationBindingBlendHint(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8708
    __real_name = "hkaAnimationBinding::BlendHint"
    local_members = ()


class hkxVertexDescriptionElementDeclDataType(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "hkxVertexDescriptionElementDecl::DataType"
    local_members = ()


class hkxVertexDescriptionElementDeclDataUsage(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "hkxVertexDescriptionElementDecl::DataUsage"
    local_members = ()


class hkxIndexBufferIndexType(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8708
    __real_name = "hkxIndexBuffer::IndexType"
    local_members = ()


class hkxMaterialUVMappingAlgorithm(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 32772
    __real_name = "hkxMaterial::UVMappingAlgorithm"
    local_members = ()


class hkxMaterialTransparency(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hkxMaterial::Transparency"
    local_members = ()


class hkxMaterialTextureStageTextureType(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 33284
    __real_name = "hkxMaterialTextureStage::TextureType"
    local_members = ()


class hknpShapeFlagsEnum(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "hknpShape::FlagsEnum"
    local_members = ()


class hknpShapeEnum(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpShape::Enum"
    local_members = ()


class hkpConstraintMotorMotorType(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8708
    __real_name = "hkpConstraintMotor::MotorType"
    local_members = ()


class hkpConstraintAtomAtomType(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "hkpConstraintAtom::AtomType"
    local_members = ()


class hkpConeLimitConstraintAtomMeasurementMode(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hkpConeLimitConstraintAtom::MeasurementMode"
    local_members = ()


class hkpBallSocketConstraintAtomSolvingMethod(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hkpBallSocketConstraintAtom::SolvingMethod"
    local_members = ()


class hknpMaterialTriggerType(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpMaterial::TriggerType"
    local_members = ()


class hknpMaterialCombinePolicy(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpMaterial::CombinePolicy"
    local_members = ()


class hknpMaterialMassChangerCategory(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpMaterial::MassChangerCategory"
    local_members = ()


class hknpMotionPropertiesFlagsEnum(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 32772
    __real_name = "hknpMotionProperties::FlagsEnum"
    local_members = ()


class hknpBodyCinfoSpuFlagsEnum(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpBodyCinfo::SpuFlagsEnum"
    local_members = ()


class hknpConstraintCinfoFlagsEnum(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpConstraintCinfo::FlagsEnum"
    local_members = ()


class hknpWorldCinfoSimulationType(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpWorldCinfo::SimulationType"
    local_members = ()


class hknpWorldCinfoLeavingBroadPhaseBehavior(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpWorldCinfo::LeavingBroadPhaseBehavior"
    local_members = ()


class hknpBodyQualityFlagsEnum(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 32772
    __real_name = "hknpBodyQuality::FlagsEnum"
    local_members = ()


class hknpCollisionFilterType(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpCollisionFilter::Type"
    local_members = ()


class hknpShapeTagCodecType(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpShapeTagCodec::Type"
    local_members = ()


class hkaSkeletonMapperDataMappingType(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 33284
    __real_name = "hkaSkeletonMapperData::MappingType"
    local_members = ()


class hkaDefaultAnimatedReferenceFrame(hkaAnimatedReferenceFrame):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __hsh = 1626923192

    local_members = (
        Member(32, "up", hkVector4),
        Member(48, "forward", hkVector4),
        Member(64, "duration", hkReal),
        Member(72, "referenceFrameSamples", hkArray(hkVector4)),
    )
    members = hkaAnimatedReferenceFrame.members + local_members

    up: hkVector4
    forward: hkVector4
    duration: float
    referenceFrameSamples: list[hkVector4]


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
    type: hkxVertexDescriptionElementDeclDataType
    usage: hkxVertexDescriptionElementDeclDataUsage
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

    indexType: hkxIndexBufferIndexType
    indices16: list[int]
    indices32: list[int]
    vertexBaseOffset: int
    length: int


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
    usageHint: hkxMaterialTextureStageTextureType
    tcoordChannel: int


class hkxVertexAnimationUsageMap(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "use", hkEnum(hkxVertexDescriptionElementDeclDataUsage, hkUint16)),
        Member(2, "useIndexOrig", hkUint8),
        Member(3, "useIndexLocal", hkUint8),
    )
    members = local_members

    use: hkxVertexDescriptionElementDeclDataUsage
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
        Member(16, "flags", hkEnum(hknpShapeFlagsEnum, hkUint16)),
        Member(18, "numShapeKeyBits", hkUint8),
        Member(19, "dispatchType", hkEnum(hknpShapeEnum, hkUint8)),
        Member(20, "convexRadius", hkReal),
        Member(24, "userData", hkUint64),
        Member(32, "properties", Ptr(hkRefCountedProperties)),
    )
    members = hkReferencedObject.members + local_members

    flags: hknpShapeFlagsEnum
    numShapeKeyBits: int
    dispatchType: hknpShapeEnum
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

    type: hkpConstraintMotorMotorType


class hkpConstraintAtom(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "type", hkEnum(hkpConstraintAtomAtomType, hkUint16)),
    )
    members = local_members

    type: hkpConstraintAtomAtomType


class hkpSetupStabilizationAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __version = 3

    local_members = (
        Member(2, "enabled", hkBool),
        Member(3, "padding", hkGenericStruct(hkUint8, 1), MemberFlags.NotSerializable),
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
        Member(64, "motors", hkGenericStruct(Ptr(hkpConstraintMotor), 3)),
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
        Member(12, "padding", hkGenericStruct(hkUint8, 4), MemberFlags.NotSerializable),
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
        Member(20, "padding", hkGenericStruct(hkUint8, 12), MemberFlags.NotSerializable),
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
        Member(20, "padding", hkGenericStruct(hkUint8, 12), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    twistAxisInA: int
    refAxisInB: int
    angleMeasurementMode: hkpConeLimitConstraintAtomMeasurementMode
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
        Member(4, "velocityStabilizationFactor", hkUFloat8, MemberFlags.Protected),
        Member(5, "enableLinearImpulseLimit", hkBool),
        Member(8, "breachImpulse", hkReal),
        Member(12, "inertiaStabilizationFactor", hkReal, MemberFlags.Protected),
    )
    members = hkpConstraintAtom.members + local_members

    solvingMethod: hkpBallSocketConstraintAtomSolvingMethod
    bodiesToNotify: int
    velocityStabilizationFactor: hkUFloat8
    enableLinearImpulseLimit: bool
    breachImpulse: float
    inertiaStabilizationFactor: float


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
    triggerType: hknpMaterialTriggerType
    triggerManifoldTolerance: hkUFloat8
    dynamicFriction: hkHalf16
    staticFriction: hkHalf16
    restitution: hkHalf16
    frictionCombinePolicy: hknpMaterialCombinePolicy
    restitutionCombinePolicy: hknpMaterialCombinePolicy
    weldingTolerance: hkHalf16
    maxContactImpulse: float
    fractionOfClippedImpulseToApply: float
    massChangerCategory: hknpMaterialMassChangerCategory
    massChangerHeavyObjectFactor: hkHalf16
    softContactForceFactor: hkHalf16
    softContactDampFactor: hkHalf16
    softContactSeperationVelocity: hkUFloat8
    surfaceVelocity: hknpSurfaceVelocity
    disablingCollisionsBetweenCvxCvxDynamicObjectsDistance: hkHalf16
    userData: int
    isShared: bool


class hknpMotionProperties(hk):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __version = 3

    local_members = (
        Member(0, "isExclusive", hkUint32),
        Member(4, "flags", hkEnum(hknpMotionPropertiesFlagsEnum, hkUint32)),
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
    flags: hknpMotionPropertiesFlagsEnum
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
        Member(80, "spuFlags", hkEnum(hknpBodyCinfoSpuFlagsEnum, hkUint8)),
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
    spuFlags: hknpBodyCinfoSpuFlagsEnum
    localFrame: hkLocalFrame


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
        Member(16, "flags", hkEnum(hknpConstraintCinfoFlagsEnum, hkUint8)),
    )
    members = local_members

    constraintData: hkpConstraintData
    bodyA: int
    bodyB: int
    flags: hknpConstraintCinfoFlagsEnum


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
        Member(4, "supportedFlags", hkEnum(hknpBodyQualityFlagsEnum, hkUint32)),
        Member(8, "requestedFlags", hkEnum(hknpBodyQualityFlagsEnum, hkUint32)),
        Member(12, "contactCachingRelativeMovementThreshold", hkReal),
    )
    members = local_members

    priority: int
    supportedFlags: hknpBodyQualityFlagsEnum
    requestedFlags: hknpBodyQualityFlagsEnum
    contactCachingRelativeMovementThreshold: float


class hknpCollisionFilter(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "type", hkEnum(hknpCollisionFilterType, hkUint8)),
    )
    members = hkReferencedObject.members + local_members

    type: hknpCollisionFilterType


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

    type: hknpShapeTagCodecType


class hkRootLevelContainerNamedVariant(hk):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr, MemberFlags.Private),
        Member(8, "className", hkStringPtr, MemberFlags.Private),
        Member(16, "variant", Ptr(hkReferencedObject), MemberFlags.Private),
    )
    members = local_members

    name: str
    className: str
    variant: hkReferencedObject


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
    floatSlots: list[hkStringPtr]
    localFrames: list[hkaSkeletonLocalFrameOnBone]
    partitions: list[hkaSkeletonPartition]


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


class hknpConvexShape(hknpShape):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(48, "vertices", hkRelArray(hkVector4)),
    )
    members = hknpShape.members + local_members

    vertices: tuple[hkVector4]


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
        Member(16, "materialAddedSignal", Ptr(_void), MemberFlags.NotSerializable),
        Member(24, "materialModifiedSignal", Ptr(_void), MemberFlags.NotSerializable),
        Member(32, "materialRemovedSignal", Ptr(_void), MemberFlags.NotSerializable),
        Member(
            40,
            "entries",
            hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations,
        ),
    )
    members = hkReferencedObject.members + local_members

    materialAddedSignal: _void
    materialModifiedSignal: _void
    materialRemovedSignal: _void
    entries: hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations


class hknpMotionPropertiesLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "entryAddedSignal", Ptr(_void), MemberFlags.NotSerializable),
        Member(24, "entryModifiedSignal", Ptr(_void), MemberFlags.NotSerializable),
        Member(32, "entryRemovedSignal", Ptr(_void), MemberFlags.NotSerializable),
        Member(
            40,
            "entries",
            hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations,
        ),
    )
    members = hkReferencedObject.members + local_members

    entryAddedSignal: _void
    entryModifiedSignal: _void
    entryRemovedSignal: _void
    entries: hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations


class hknpBodyQualityLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 544
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "qualityModifiedSignal", Ptr(_void), MemberFlags.NotSerializable),
        Member(32, "qualities", hkGenericStruct(hknpBodyQuality, 32)),
    )
    members = hkReferencedObject.members + local_members

    qualityModifiedSignal: _void
    qualities: tuple[hknpBodyQuality, ...]


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
        Member(
            32,
            "simpleMappingPartitionRanges",
            hkArray(hkaSkeletonMapperDataPartitionMappingRange),
        ),
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
    mappingType: hkaSkeletonMapperDataMappingType


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


class hkaAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __version = 3

    local_members = (
        Member(16, "type", hkEnum(hkaAnimationAnimationType, hkInt32), MemberFlags.Protected),
        Member(20, "duration", hkReal),
        Member(24, "numberOfTransformTracks", hkInt32),
        Member(28, "numberOfFloatTracks", hkInt32),
        Member(32, "extractedMotion", Ptr(hkaAnimatedReferenceFrame), MemberFlags.Protected),
        Member(40, "annotationTracks", hkArray(hkaAnnotationTrack)),
    )
    members = hkReferencedObject.members + local_members

    type: hkaAnimationAnimationType
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

    __hsh = 263164240
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
    blendHint: hkaAnimationBindingBlendHint


class hkxVertexBuffer(hkReferencedObject):
    alignment = 16
    byte_size = 136
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __version = 1

    local_members = (
        Member(16, "data", hkxVertexBufferVertexData, MemberFlags.Protected),
        Member(120, "desc", hkxVertexDescription, MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    data: hkxVertexBufferVertexData
    desc: hkxVertexDescription


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

    planes: tuple[hkVector4]
    faces: tuple[hknpConvexPolytopeShapeFace]
    indices: tuple[hkUint8]


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
        Member(8, "userBodyBuffer", Ptr(_void), MemberFlags.NotSerializable),
        Member(16, "motionBufferCapacity", hkInt32),
        Member(24, "userMotionBuffer", Ptr(_void), MemberFlags.NotSerializable),
        Member(32, "constraintBufferCapacity", hkInt32),
        Member(40, "userConstraintBuffer", Ptr(_void), MemberFlags.NotSerializable),
        Member(48, "persistentStreamAllocator", Ptr(_void), MemberFlags.NotSerializable),
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
    userBodyBuffer: _void
    motionBufferCapacity: int
    userMotionBuffer: _void
    constraintBufferCapacity: int
    userConstraintBuffer: _void
    persistentStreamAllocator: _void
    materialLibrary: hknpMaterialLibrary
    motionPropertiesLibrary: hknpMotionPropertiesLibrary
    qualityLibrary: hknpBodyQualityLibrary
    simulationType: hknpWorldCinfoSimulationType
    numSplitterCells: int
    gravity: hkVector4
    enableContactCaching: bool
    mergeEventsBeforeDispatch: bool
    leavingBroadPhaseBehavior: hknpWorldCinfoLeavingBroadPhaseBehavior
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


class hkaSplineCompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __hsh = 2352701310

    local_members = (
        Member(56, "numFrames", _int, MemberFlags.Private),
        Member(60, "numBlocks", _int, MemberFlags.Private),
        Member(64, "maxFramesPerBlock", _int, MemberFlags.Private),
        Member(68, "maskAndQuantizationSize", _int, MemberFlags.Private),
        Member(72, "blockDuration", hkReal, MemberFlags.Private),
        Member(76, "blockInverseDuration", hkReal, MemberFlags.Private),
        Member(80, "frameDuration", hkReal, MemberFlags.Private),
        Member(88, "blockOffsets", hkArray(hkUint32), MemberFlags.Private),
        Member(104, "floatBlockOffsets", hkArray(hkUint32), MemberFlags.Private),
        Member(120, "transformOffsets", hkArray(hkUint32), MemberFlags.Private),
        Member(136, "floatOffsets", hkArray(hkUint32), MemberFlags.Private),
        Member(152, "data", hkArray(hkUint8), MemberFlags.Private),
        Member(168, "endian", _int, MemberFlags.Private),
    )
    members = hkaAnimation.members + local_members

    numFrames: int
    numBlocks: int
    maxFramesPerBlock: int
    maskAndQuantizationSize: int
    blockDuration: float
    blockInverseDuration: float
    frameDuration: float
    blockOffsets: list[int]
    floatBlockOffsets: list[int]
    transformOffsets: list[int]
    floatOffsets: list[int]
    data: list[int]
    endian: int


class hkaInterleavedUncompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 96
    tag_format_flags = 45
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __hsh = 3449291259
    __version = 1

    local_members = (
        Member(56, "transforms", hkArray(hkQsTransform)),
        Member(72, "floats", hkArray(hkReal)),
    )
    members = hkaAnimation.members + local_members

    transforms: list[hkQsTransform]
    floats: list[float]


class hkaQuantizedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __hsh = 213316226

    local_members = (
        Member(56, "data", hkArray(hkUint8), MemberFlags.Private),
        Member(72, "endian", hkUint32, MemberFlags.Private),
        Member(80, "skeleton", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkaAnimation.members + local_members

    data: list[int]
    endian: int
    skeleton: hkReflectDetailOpaque


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
        Member(152, "uvMapScale", hkGenericStruct(hkReal, 2)),
        Member(160, "uvMapOffset", hkGenericStruct(hkReal, 2)),
        Member(168, "uvMapRotation", hkReal),
        Member(172, "uvMapAlgorithm", hkEnum(hkxMaterialUVMappingAlgorithm, hkUint32)),
        Member(176, "specularMultiplier", hkReal),
        Member(180, "specularExponent", hkReal),
        Member(184, "transparency", hkEnum(hkxMaterialTransparency, hkUint8)),
        Member(192, "userData", hkUlong),
        Member(200, "properties", hkArray(hkxMaterialProperty), MemberFlags.Protected),
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
    uvMapAlgorithm: hkxMaterialUVMappingAlgorithm
    specularMultiplier: float
    specularExponent: float
    transparency: hkxMaterialTransparency
    userData: int
    properties: list[hkxMaterialProperty]


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
        Member(16, "skeletons", hkArray(hkRefPtr(hkaSkeleton))),
        Member(32, "animations", hkArray(hkRefPtr(hkaAnimation))),
        Member(48, "bindings", hkArray(hkRefPtr(hkaAnimationBinding))),
        Member(64, "attachments", hkArray(hkRefPtr(hkaBoneAttachment))),
        Member(80, "skins", hkArray(hkRefPtr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]


class hkp2dAngConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(2, "freeRotationAxis", hkUint8),
        Member(3, "padding", hkStruct(hkUint8, 13)),
    )

    freeRotationAxis: int
    padding: tuple[hkUint8]


class hkpAngMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __version = 1

    local_members = (
        Member(2, "isEnabled", hkBool),
        Member(3, "motorAxis", hkUint8),
        Member(4, "initializedOffset", hkInt16),
        Member(6, "previousTargetAngleOffset", hkInt16),
        Member(8, "correspondingAngLimitSolverResultOffset", hkInt16),
        Member(12, "targetAngle", hkReal),
        Member(16, "motor", Ptr(hkpConstraintMotor)),
        Member(24, "padding", hkStruct(hkUint8, 20)),
    )


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


class hkpLimitedHingeConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 304
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    __hsh = 1374314554

    local_members = (
        Member(32, "atoms", hkpLimitedHingeConstraintDataAtoms),
    )
