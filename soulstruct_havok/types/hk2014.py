"""Auto-generated types for Havok 2014."""
from __future__ import annotations
import typing as tp

from soulstruct_havok.types.core import *

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.tagfile.structs import TagFileItem
    from soulstruct_havok.packfile.structs import PackFileItemEntry


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
        Member(0, "vec", hkVector4f, flags=32),
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
        Member(0, "col0", hkVector4f, flags=34),
        Member(16, "col1", hkVector4f, flags=34),
        Member(32, "col2", hkVector4f, flags=34),
        Member(48, "col3", hkVector4f, flags=34),
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
        Member(0, "rotation", hkRotationf, flags=34),
        Member(48, "translation", hkVector4f, flags=34),
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
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "translation", hkVector4f, flags=32),
        Member(16, "rotation", hkQuaternionf, flags=32),
        Member(32, "scale", hkVector4f, flags=32),
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
    tag_format_flags = 41
    tag_type_flags = 7
    local_members = ()


class hkReferencedObject(hkBaseObject):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(8, "memSizeAndRefCount", hkUint32, flags=1024),
    )
    members = hkBaseObject.members + local_members

    memSizeAndRefCount: hkUint32


class hkRefVariant(hk):
    alignment = 8
    byte_size = 8
    tag_format_flags = 43
    tag_type_flags = 6

    __hsh = 2872857893

    local_members = (
        Member(0, "ptr", Ptr(hkReferencedObject), flags=36),
    )
    members = local_members

    ptr: hkReferencedObject


class hkLocalFrame(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7
    local_members = ()


class hkaAnimatedReferenceFrame(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(12, "frameType", hkInt8, flags=33),
    )
    members = hkReferencedObject.members + local_members

    frameType: hkInt8


class hkxVertexBufferVertexData(hk):
    alignment = 16
    byte_size = 104
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 2

    local_members = (
        Member(0, "vectorData", hkArray(hkUint32), flags=32),
        Member(16, "floatData", hkArray(hkUint32), flags=32),
        Member(32, "uint32Data", hkArray(hkUint32), flags=32),
        Member(48, "uint16Data", hkArray(hkUint16), flags=32),
        Member(64, "uint8Data", hkArray(hkUint8), flags=32),
        Member(80, "numVerts", hkUint32, flags=32),
        Member(84, "vectorStride", hkUint32, flags=32),
        Member(88, "floatStride", hkUint32, flags=32),
        Member(92, "uint32Stride", hkUint32, flags=32),
        Member(96, "uint16Stride", hkUint32, flags=32),
        Member(100, "uint8Stride", hkUint32, flags=32),
    )
    members = local_members

    vectorData: list[hkUint32]
    floatData: list[hkUint32]
    uint32Data: list[hkUint32]
    uint16Data: list[hkUint16]
    uint8Data: list[hkUint8]
    numVerts: hkUint32
    vectorStride: hkUint32
    floatStride: hkUint32
    uint32Stride: hkUint32
    uint16Stride: hkUint32
    uint8Stride: hkUint32


class hkxMaterialProperty(hk):
    alignment = 8
    byte_size = 8
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "key", hkUint32, flags=32),
        Member(4, "value", hkUint32, flags=32),
    )
    members = local_members

    key: hkUint32
    value: hkUint32


class hkMeshBoneIndexMapping(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "mapping", hkArray(hkInt16), flags=32),
    )
    members = local_members

    mapping: list[hkInt16]


class hkaMeshBindingMapping(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "mapping", hkArray(hkInt16), flags=32),
    )
    members = local_members

    mapping: list[hkInt16]


class hkCompressedMassProperties(hk):
    alignment = 16
    byte_size = 32
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "centerOfMass", hkGenericStruct(hkInt16, 4), flags=0),
        Member(8, "inertia", hkGenericStruct(hkInt16, 4), flags=0),
        Member(16, "majorAxisSpace", hkGenericStruct(hkInt16, 4), flags=0),
        Member(24, "mass", hkReal, flags=0),
        Member(28, "volume", hkReal, flags=0),
    )
    members = local_members

    centerOfMass: tuple[hkInt16, ...]
    inertia: tuple[hkInt16, ...]
    majorAxisSpace: tuple[hkInt16, ...]
    mass: hkReal
    volume: hkReal


class hkRefCountedPropertiesEntry(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "object", Ptr(hkReferencedObject), flags=0),
        Member(8, "key", hkUint16, flags=0),
        Member(10, "flags", hkUint16, flags=0),
    )
    members = local_members

    object: hkReferencedObject
    key: hkUint16
    flags: hkUint16


class hknpConvexPolytopeShapeFace(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "firstIndex", hkUint16, flags=0),
        Member(2, "numIndices", hkUint8, flags=0),
        Member(3, "minHalfAngle", hkUint8, flags=0),
    )
    members = local_members

    firstIndex: hkUint16
    numIndices: hkUint8
    minHalfAngle: hkUint8


class hkpConstraintData(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(16, "userData", hkUlong, flags=32),
    )
    members = hkReferencedObject.members + local_members

    userData: hkUlong


class hkUFloat8(hk):
    alignment = 2
    byte_size = 1
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "value", hkUint8, flags=32),
    )
    members = local_members

    value: hkUint8


class hknpSurfaceVelocity(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7
    local_members = ()


class hkAabb(hk):
    alignment = 16
    byte_size = 32
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "min", hkVector4, flags=32),
        Member(16, "max", hkVector4, flags=32),
    )
    members = local_members

    min: hkVector4
    max: hkVector4


class hknpBroadPhaseConfig(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7
    local_members = ()


class hkaSkeletonMapperDataPartitionMappingRange(hk):
    alignment = 8
    byte_size = 8
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "startMappingIndex", hkInt32, flags=32),
        Member(4, "numMappings", hkInt32, flags=32),
    )
    members = local_members

    startMappingIndex: hkInt32
    numMappings: hkInt32


class hkaSkeletonMapperDataSimpleMapping(hk):
    alignment = 16
    byte_size = 64
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "boneA", hkInt16, flags=32),
        Member(2, "boneB", hkInt16, flags=32),
        Member(16, "aFromBTransform", hkQsTransform, flags=32),
    )
    members = local_members

    boneA: hkInt16
    boneB: hkInt16
    aFromBTransform: hkQsTransform


class hkaSkeletonMapperDataChainMapping(hk):
    alignment = 16
    byte_size = 112
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "startBoneA", hkInt16, flags=32),
        Member(2, "endBoneA", hkInt16, flags=32),
        Member(4, "startBoneB", hkInt16, flags=32),
        Member(6, "endBoneB", hkInt16, flags=32),
        Member(16, "startAFromBTransform", hkQsTransform, flags=32),
        Member(64, "endAFromBTransform", hkQsTransform, flags=32),
    )
    members = local_members

    startBoneA: hkInt16
    endBoneA: hkInt16
    startBoneB: hkInt16
    endBoneB: hkInt16
    startAFromBTransform: hkQsTransform
    endAFromBTransform: hkQsTransform


class hkContainerHeapAllocator(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 57
    tag_type_flags = 7

    __abstract_value = 16
    local_members = ()


class hkStringPtr(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 41
    tag_type_flags = 3

    __hsh = 2837000324

    local_members = (
        Member(0, "stringAndFlag", _const_char, flags=36),
    )
    members = local_members

    stringAndFlag: _const_char


class hkBool(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 41
    tag_type_flags = 8194

    local_members = (
        Member(0, "bool", _char, flags=36),
    )
    members = local_members

    bool: _char


class hkHalf16(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 41
    tag_type_flags = 476677

    local_members = (
        Member(0, "value", hkInt16, flags=36),
    )
    members = local_members

    value: hkInt16


class hkaAnimationAnimationType(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 33284
    __real_name = "hkaAnimation::AnimationType"
    local_members = ()


class hkaAnimationBindingBlendHint(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8708
    __real_name = "hkaAnimationBinding::BlendHint"
    local_members = ()


class hkxVertexDescriptionElementDeclDataType(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "hkxVertexDescriptionElementDecl::DataType"
    local_members = ()


class hkxVertexDescriptionElementDeclDataUsage(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "hkxVertexDescriptionElementDecl::DataUsage"
    local_members = ()


class hkxIndexBufferIndexType(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8708
    __real_name = "hkxIndexBuffer::IndexType"
    local_members = ()


class hkxMaterialUVMappingAlgorithm(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 32772
    __real_name = "hkxMaterial::UVMappingAlgorithm"
    local_members = ()


class hkxMaterialTransparency(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hkxMaterial::Transparency"
    local_members = ()


class hkxMaterialTextureStageTextureType(hk):
    alignment = 0
    byte_size = 0
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
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpShape::Enum"
    local_members = ()


class hkpConstraintMotorMotorType(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8708
    __real_name = "hkpConstraintMotor::MotorType"
    local_members = ()


class hkpConstraintAtomAtomType(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "hkpConstraintAtom::AtomType"
    local_members = ()


class hkpConeLimitConstraintAtomMeasurementMode(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hkpConeLimitConstraintAtom::MeasurementMode"
    local_members = ()


class hkpBallSocketConstraintAtomSolvingMethod(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hkpBallSocketConstraintAtom::SolvingMethod"
    local_members = ()


class hknpMaterialTriggerType(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpMaterial::TriggerType"
    local_members = ()


class hknpMaterialCombinePolicy(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpMaterial::CombinePolicy"
    local_members = ()


class hknpMaterialMassChangerCategory(hk):
    alignment = 0
    byte_size = 0
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
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpWorldCinfo::SimulationType"
    local_members = ()


class hknpWorldCinfoLeavingBroadPhaseBehavior(hk):
    alignment = 0
    byte_size = 0
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
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpCollisionFilter::Type"
    local_members = ()


class hknpShapeTagCodecType(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "hknpShapeTagCodec::Type"
    local_members = ()


class hkaSkeletonMapperDataMappingType(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 33284
    __real_name = "hkaSkeletonMapperData::MappingType"
    local_members = ()


class hkaDefaultAnimatedReferenceFrame(hkaAnimatedReferenceFrame):
    alignment = 16
    byte_size = 96
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 1626923192

    local_members = (
        Member(32, "up", hkVector4, flags=32),
        Member(48, "forward", hkVector4, flags=32),
        Member(64, "duration", hkReal, flags=32),
        Member(72, "referenceFrameSamples", hkArray(hkVector4), flags=32),
    )
    members = hkaAnimatedReferenceFrame.members + local_members

    up: hkVector4
    forward: hkVector4
    duration: hkReal
    referenceFrameSamples: list[hkVector4]


class hkaBone(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "name", hkStringPtr, flags=32),
        Member(8, "lockTranslation", hkBool, flags=32),
    )
    members = local_members

    name: hkStringPtr
    lockTranslation: hkBool


class hkaSkeletonLocalFrameOnBone(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "localFrame", Ptr(hkLocalFrame), flags=32),
        Member(8, "boneIndex", hkInt16, flags=32),
    )
    members = local_members

    localFrame: hkLocalFrame
    boneIndex: hkInt16


class hkaSkeletonPartition(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr, flags=32),
        Member(8, "startBoneIndex", hkInt16, flags=32),
        Member(10, "numBones", hkInt16, flags=32),
    )
    members = local_members

    name: hkStringPtr
    startBoneIndex: hkInt16
    numBones: hkInt16


class hkaAnnotationTrackAnnotation(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "time", hkReal, flags=32),
        Member(8, "text", hkStringPtr, flags=32),
    )
    members = local_members

    time: hkReal
    text: hkStringPtr


class hkaBoneAttachment(hkReferencedObject):
    alignment = 16
    byte_size = 128
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 2

    local_members = (
        Member(16, "originalSkeletonName", hkStringPtr, flags=32),
        Member(32, "boneFromAttachment", hkMatrix4, flags=32),
        Member(96, "attachment", Ptr(hkReferencedObject), flags=32),
        Member(104, "name", hkStringPtr, flags=32),
        Member(112, "boneIndex", hkInt16, flags=32),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: hkStringPtr
    boneFromAttachment: hkMatrix4
    attachment: hkReferencedObject
    name: hkStringPtr
    boneIndex: hkInt16


class hkxVertexDescriptionElementDecl(hk):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 4

    local_members = (
        Member(0, "byteOffset", hkUint32, flags=32),
        Member(4, "type", hkEnum(hkxVertexDescriptionElementDeclDataType, hkUint16), flags=32),
        Member(6, "usage", hkEnum(hkxVertexDescriptionElementDeclDataUsage, hkUint16), flags=32),
        Member(8, "byteStride", hkUint32, flags=32),
        Member(12, "numElements", hkUint8, flags=32),
        Member(16, "channelID", hkStringPtr, flags=32),
    )
    members = local_members

    byteOffset: hkUint32
    type: hkxVertexDescriptionElementDeclDataType
    usage: hkxVertexDescriptionElementDeclDataUsage
    byteStride: hkUint32
    numElements: hkUint8
    channelID: hkStringPtr


class hkxIndexBuffer(hkReferencedObject):
    alignment = 16
    byte_size = 56
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(12, "indexType", hkEnum(hkxIndexBufferIndexType, hkInt8), flags=32),
        Member(16, "indices16", hkArray(hkUint16), flags=32),
        Member(32, "indices32", hkArray(hkUint32), flags=32),
        Member(48, "vertexBaseOffset", hkUint32, flags=32),
        Member(52, "length", hkUint32, flags=32),
    )
    members = hkReferencedObject.members + local_members

    indexType: hkxIndexBufferIndexType
    indices16: list[hkUint16]
    indices32: list[hkUint32]
    vertexBaseOffset: hkUint32
    length: hkUint32


class hkxAttribute(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr, flags=32),
        Member(8, "value", Ptr(hkReferencedObject), flags=32),
    )
    members = local_members

    name: hkStringPtr
    value: hkReferencedObject


class hkxMaterialTextureStage(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "texture", Ptr(hkReferencedObject), flags=32),
        Member(8, "usageHint", hkEnum(hkxMaterialTextureStageTextureType, hkInt32), flags=32),
        Member(12, "tcoordChannel", hkInt32, flags=32),
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: hkxMaterialTextureStageTextureType
    tcoordChannel: hkInt32


class hkxVertexAnimationUsageMap(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "use", hkEnum(hkxVertexDescriptionElementDeclDataUsage, hkUint16), flags=32),
        Member(2, "useIndexOrig", hkUint8, flags=32),
        Member(3, "useIndexLocal", hkUint8, flags=32),
    )
    members = local_members

    use: hkxVertexDescriptionElementDeclDataUsage
    useIndexOrig: hkUint8
    useIndexLocal: hkUint8


class hknpShapeMassProperties(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 3910735656

    local_members = (
        Member(16, "compressedMassProperties", hkCompressedMassProperties, flags=128),
    )
    members = hkReferencedObject.members + local_members

    compressedMassProperties: hkCompressedMassProperties


class hkRefCountedProperties(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 2086094951
    __version = 1

    local_members = (
        Member(0, "entries", hkArray(hkRefCountedPropertiesEntry), flags=0),
    )
    members = local_members

    entries: list[hkRefCountedPropertiesEntry]


class hknpShape(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 2

    local_members = (
        Member(16, "flags", hkEnum(hknpShapeFlagsEnum, hkUint16), flags=256),
        Member(18, "numShapeKeyBits", hkUint8, flags=0),
        Member(19, "dispatchType", hkEnum(hknpShapeEnum, hkUint8), flags=0),
        Member(20, "convexRadius", hkReal, flags=0),
        Member(24, "userData", hkUint64, flags=0),
        Member(32, "properties", Ptr(hkRefCountedProperties), flags=0),
    )
    members = hkReferencedObject.members + local_members

    flags: hknpShapeFlagsEnum
    numShapeKeyBits: hkUint8
    dispatchType: hknpShapeEnum
    convexRadius: hkReal
    userData: hkUint64
    properties: hkRefCountedProperties


class hkpConstraintMotor(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(12, "type", hkEnum(hkpConstraintMotorMotorType, hkInt8), flags=32),
    )
    members = hkReferencedObject.members + local_members

    type: hkpConstraintMotorMotorType


class hkpConstraintAtom(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "type", hkEnum(hkpConstraintAtomAtomType, hkUint16), flags=32),
    )
    members = local_members

    type: hkpConstraintAtomAtomType


class hkpSetupStabilizationAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 3

    local_members = (
        Member(2, "enabled", hkBool, flags=32),
        Member(3, "padding", hkGenericStruct(hkUint8, 1), flags=1024),
        Member(4, "maxLinImpulse", hkReal, flags=32),
        Member(8, "maxAngImpulse", hkReal, flags=32),
        Member(12, "maxAngle", hkReal, flags=32),
    )
    members = hkpConstraintAtom.members + local_members

    enabled: hkBool
    padding: tuple[hkUint8, ...]
    maxLinImpulse: hkReal
    maxAngImpulse: hkReal
    maxAngle: hkReal


class hkpRagdollMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 96
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(2, "isEnabled", hkBool, flags=32),
        Member(4, "initializedOffset", hkInt16, flags=33),
        Member(6, "previousTargetAnglesOffset", hkInt16, flags=33),
        Member(16, "target_bRca", hkMatrix3, flags=32),
        Member(64, "motors", hkGenericStruct(Ptr(hkpConstraintMotor), 3), flags=32),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: hkBool
    initializedOffset: hkInt16
    previousTargetAnglesOffset: hkInt16
    target_bRca: hkMatrix3
    motors: tuple[hkpConstraintMotor, ...]


class hkpAngFrictionConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(2, "isEnabled", hkUint8, flags=32),
        Member(3, "firstFrictionAxis", hkUint8, flags=32),
        Member(4, "numFrictionAxes", hkUint8, flags=32),
        Member(8, "maxFrictionTorque", hkReal, flags=32),
        Member(12, "padding", hkGenericStruct(hkUint8, 4), flags=1024),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: hkUint8
    firstFrictionAxis: hkUint8
    numFrictionAxes: hkUint8
    maxFrictionTorque: hkReal
    padding: tuple[hkUint8, ...]


class hkpTwistLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(2, "isEnabled", hkUint8, flags=32),
        Member(3, "twistAxis", hkUint8, flags=32),
        Member(4, "refAxis", hkUint8, flags=32),
        Member(8, "minAngle", hkReal, flags=32),
        Member(12, "maxAngle", hkReal, flags=32),
        Member(16, "angularLimitsTauFactor", hkReal, flags=32),
        Member(20, "padding", hkGenericStruct(hkUint8, 12), flags=1024),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: hkUint8
    twistAxis: hkUint8
    refAxis: hkUint8
    minAngle: hkReal
    maxAngle: hkReal
    angularLimitsTauFactor: hkReal
    padding: tuple[hkUint8, ...]


class hkpConeLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(2, "isEnabled", hkUint8, flags=32),
        Member(3, "twistAxisInA", hkUint8, flags=32),
        Member(4, "refAxisInB", hkUint8, flags=32),
        Member(5, "angleMeasurementMode", hkEnum(hkpConeLimitConstraintAtomMeasurementMode, hkUint8), flags=32),
        Member(6, "memOffsetToAngleOffset", hkUint8, flags=32),
        Member(8, "minAngle", hkReal, flags=32),
        Member(12, "maxAngle", hkReal, flags=32),
        Member(16, "angularLimitsTauFactor", hkReal, flags=32),
        Member(20, "padding", hkGenericStruct(hkUint8, 12), flags=1024),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: hkUint8
    twistAxisInA: hkUint8
    refAxisInB: hkUint8
    angleMeasurementMode: hkpConeLimitConstraintAtomMeasurementMode
    memOffsetToAngleOffset: hkUint8
    minAngle: hkReal
    maxAngle: hkReal
    angularLimitsTauFactor: hkReal
    padding: tuple[hkUint8, ...]


class hkpBallSocketConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 5

    local_members = (
        Member(2, "solvingMethod", hkEnum(hkpBallSocketConstraintAtomSolvingMethod, hkUint8), flags=32),
        Member(3, "bodiesToNotify", hkUint8, flags=32),
        Member(4, "velocityStabilizationFactor", hkUFloat8, flags=34),
        Member(5, "enableLinearImpulseLimit", hkBool, flags=32),
        Member(8, "breachImpulse", hkReal, flags=32),
        Member(12, "inertiaStabilizationFactor", hkReal, flags=34),
    )
    members = hkpConstraintAtom.members + local_members

    solvingMethod: hkpBallSocketConstraintAtomSolvingMethod
    bodiesToNotify: hkUint8
    velocityStabilizationFactor: hkUFloat8
    enableLinearImpulseLimit: hkBool
    breachImpulse: hkReal
    inertiaStabilizationFactor: hkReal


class hknpMaterial(hk):
    alignment = 16
    byte_size = 80
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr, flags=256),
        Member(8, "isExclusive", hkUint32, flags=0),
        Member(12, "flags", hkInt32, flags=0),
        Member(16, "triggerType", hkEnum(hknpMaterialTriggerType, hkUint8), flags=0),
        Member(17, "triggerManifoldTolerance", hkUFloat8, flags=0),
        Member(18, "dynamicFriction", hkHalf16, flags=0),
        Member(20, "staticFriction", hkHalf16, flags=0),
        Member(22, "restitution", hkHalf16, flags=0),
        Member(24, "frictionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8), flags=0),
        Member(25, "restitutionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8), flags=0),
        Member(26, "weldingTolerance", hkHalf16, flags=0),
        Member(28, "maxContactImpulse", hkReal, flags=0),
        Member(32, "fractionOfClippedImpulseToApply", hkReal, flags=0),
        Member(36, "massChangerCategory", hkEnum(hknpMaterialMassChangerCategory, hkUint8), flags=0),
        Member(38, "massChangerHeavyObjectFactor", hkHalf16, flags=0),
        Member(40, "softContactForceFactor", hkHalf16, flags=0),
        Member(42, "softContactDampFactor", hkHalf16, flags=0),
        Member(44, "softContactSeperationVelocity", hkUFloat8, flags=0),
        Member(48, "surfaceVelocity", Ptr(hknpSurfaceVelocity), flags=0),
        Member(56, "disablingCollisionsBetweenCvxCvxDynamicObjectsDistance", hkHalf16, flags=0),
        Member(64, "userData", hkUint64, flags=128),
        Member(72, "isShared", hkBool, flags=0),
    )
    members = local_members

    name: hkStringPtr
    isExclusive: hkUint32
    flags: hkInt32
    triggerType: hknpMaterialTriggerType
    triggerManifoldTolerance: hkUFloat8
    dynamicFriction: hkHalf16
    staticFriction: hkHalf16
    restitution: hkHalf16
    frictionCombinePolicy: hknpMaterialCombinePolicy
    restitutionCombinePolicy: hknpMaterialCombinePolicy
    weldingTolerance: hkHalf16
    maxContactImpulse: hkReal
    fractionOfClippedImpulseToApply: hkReal
    massChangerCategory: hknpMaterialMassChangerCategory
    massChangerHeavyObjectFactor: hkHalf16
    softContactForceFactor: hkHalf16
    softContactDampFactor: hkHalf16
    softContactSeperationVelocity: hkUFloat8
    surfaceVelocity: hknpSurfaceVelocity
    disablingCollisionsBetweenCvxCvxDynamicObjectsDistance: hkHalf16
    userData: hkUint64
    isShared: hkBool


class hknpMotionProperties(hk):
    alignment = 16
    byte_size = 64
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 3

    local_members = (
        Member(0, "isExclusive", hkUint32, flags=256),
        Member(4, "flags", hkEnum(hknpMotionPropertiesFlagsEnum, hkUint32), flags=0),
        Member(8, "gravityFactor", hkReal, flags=0),
        Member(12, "timeFactor", hkReal, flags=0),
        Member(16, "maxLinearSpeed", hkReal, flags=0),
        Member(20, "maxAngularSpeed", hkReal, flags=0),
        Member(24, "linearDamping", hkReal, flags=0),
        Member(28, "angularDamping", hkReal, flags=0),
        Member(32, "solverStabilizationSpeedThreshold", hkReal, flags=0),
        Member(36, "solverStabilizationSpeedReduction", hkReal, flags=0),
        Member(40, "maxDistSqrd", hkReal, flags=0),
        Member(44, "maxRotSqrd", hkReal, flags=0),
        Member(48, "invBlockSize", hkReal, flags=0),
        Member(52, "pathingUpperThreshold", hkInt16, flags=0),
        Member(54, "pathingLowerThreshold", hkInt16, flags=0),
        Member(56, "numDeactivationFrequencyPasses", hkUint8, flags=0),
        Member(57, "deactivationVelocityScaleSquare", hkUint8, flags=0),
        Member(58, "minimumPathingVelocityScaleSquare", hkUint8, flags=0),
        Member(59, "spikingVelocityScaleThresholdSquared", hkUint8, flags=0),
        Member(60, "minimumSpikingVelocityScaleSquared", hkUint8, flags=0),
    )
    members = local_members

    isExclusive: hkUint32
    flags: hknpMotionPropertiesFlagsEnum
    gravityFactor: hkReal
    timeFactor: hkReal
    maxLinearSpeed: hkReal
    maxAngularSpeed: hkReal
    linearDamping: hkReal
    angularDamping: hkReal
    solverStabilizationSpeedThreshold: hkReal
    solverStabilizationSpeedReduction: hkReal
    maxDistSqrd: hkReal
    maxRotSqrd: hkReal
    invBlockSize: hkReal
    pathingUpperThreshold: hkInt16
    pathingLowerThreshold: hkInt16
    numDeactivationFrequencyPasses: hkUint8
    deactivationVelocityScaleSquare: hkUint8
    minimumPathingVelocityScaleSquare: hkUint8
    spikingVelocityScaleThresholdSquared: hkUint8
    minimumSpikingVelocityScaleSquared: hkUint8


class hknpMotionCinfo(hk):
    alignment = 16
    byte_size = 112
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "motionPropertiesId", hkUint16, flags=0),
        Member(2, "enableDeactivation", hkBool, flags=0),
        Member(4, "inverseMass", hkReal, flags=0),
        Member(8, "massFactor", hkReal, flags=0),
        Member(12, "maxLinearAccelerationDistancePerStep", hkReal, flags=0),
        Member(16, "maxRotationToPreventTunneling", hkReal, flags=0),
        Member(32, "inverseInertiaLocal", hkVector4, flags=0),
        Member(48, "centerOfMassWorld", hkVector4, flags=0),
        Member(64, "orientation", hkQuaternionf, flags=0),
        Member(80, "linearVelocity", hkVector4, flags=0),
        Member(96, "angularVelocity", hkVector4, flags=0),
    )
    members = local_members

    motionPropertiesId: hkUint16
    enableDeactivation: hkBool
    inverseMass: hkReal
    massFactor: hkReal
    maxLinearAccelerationDistancePerStep: hkReal
    maxRotationToPreventTunneling: hkReal
    inverseInertiaLocal: hkVector4
    centerOfMassWorld: hkVector4
    orientation: hkQuaternionf
    linearVelocity: hkVector4
    angularVelocity: hkVector4


class hknpBodyCinfo(hk):
    alignment = 16
    byte_size = 96
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 2

    local_members = (
        Member(0, "shape", Ptr(hknpShape), flags=512),
        Member(8, "reservedBodyId", hkUint32, flags=0),
        Member(12, "motionId", hkUint32, flags=0),
        Member(16, "qualityId", hkUint8, flags=0),
        Member(18, "materialId", hkUint16, flags=0),
        Member(20, "collisionFilterInfo", hkUint32, flags=0),
        Member(24, "flags", hkInt32, flags=0),
        Member(28, "collisionLookAheadDistance", hkReal, flags=0),
        Member(32, "name", hkStringPtr, flags=0),
        Member(40, "userData", hkUint64, flags=0),
        Member(48, "position", hkVector4, flags=0),
        Member(64, "orientation", hkQuaternionf, flags=0),
        Member(80, "spuFlags", hkEnum(hknpBodyCinfoSpuFlagsEnum, hkUint8), flags=0),
        Member(88, "localFrame", Ptr(hkLocalFrame), flags=0),
    )
    members = local_members

    shape: hknpShape
    reservedBodyId: hkUint32
    motionId: hkUint32
    qualityId: hkUint8
    materialId: hkUint16
    collisionFilterInfo: hkUint32
    flags: hkInt32
    collisionLookAheadDistance: hkReal
    name: hkStringPtr
    userData: hkUint64
    position: hkVector4
    orientation: hkQuaternionf
    spuFlags: hknpBodyCinfoSpuFlagsEnum
    localFrame: hkLocalFrame


class hknpConstraintCinfo(hk):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 2

    local_members = (
        Member(0, "constraintData", Ptr(hkpConstraintData), flags=0),
        Member(8, "bodyA", hkUint32, flags=0),
        Member(12, "bodyB", hkUint32, flags=0),
        Member(16, "flags", hkEnum(hknpConstraintCinfoFlagsEnum, hkUint8), flags=0),
    )
    members = local_members

    constraintData: hkpConstraintData
    bodyA: hkUint32
    bodyB: hkUint32
    flags: hknpConstraintCinfoFlagsEnum


class hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations(hk):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "elements", hkArray(hknpMaterial), flags=0),
        Member(16, "firstFree", hkInt32, flags=0),
    )
    members = local_members

    elements: list[hknpMaterial]
    firstFree: hkInt32


class hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations(hk):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "elements", hkArray(hknpMotionProperties), flags=0),
        Member(16, "firstFree", hkInt32, flags=0),
    )
    members = local_members

    elements: list[hknpMotionProperties]
    firstFree: hkInt32


class hknpBodyQuality(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "priority", hkInt32, flags=0),
        Member(4, "supportedFlags", hkEnum(hknpBodyQualityFlagsEnum, hkUint32), flags=0),
        Member(8, "requestedFlags", hkEnum(hknpBodyQualityFlagsEnum, hkUint32), flags=0),
        Member(12, "contactCachingRelativeMovementThreshold", hkReal, flags=0),
    )
    members = local_members

    priority: hkInt32
    supportedFlags: hknpBodyQualityFlagsEnum
    requestedFlags: hknpBodyQualityFlagsEnum
    contactCachingRelativeMovementThreshold: hkReal


class hknpCollisionFilter(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(12, "type", hkEnum(hknpCollisionFilterType, hkUint8), flags=0),
    )
    members = hkReferencedObject.members + local_members

    type: hknpCollisionFilterType


class hknpShapeTagCodec(hkReferencedObject):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(12, "type", hkEnum(hknpShapeTagCodecType, hkUint8), flags=0),
    )
    members = hkReferencedObject.members + local_members

    type: hknpShapeTagCodecType


class hkRootLevelContainerNamedVariant(hk):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr, flags=36),
        Member(8, "className", hkStringPtr, flags=36),
        Member(16, "variant", Ptr(hkReferencedObject), flags=36),
    )
    members = local_members

    name: hkStringPtr
    className: hkStringPtr
    variant: hkReferencedObject

    @classmethod
    def unpack(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> hk:
        reader.seek(offset)
        return unpack_named_variant(cls, reader, items, globals())
        
    @classmethod
    def unpack_packfile(cls, entry: PackFileItemEntry, offset: int = None, pointer_size=8) -> hk:
        if offset is not None:
            entry.reader.seek(offset)
        return unpack_named_variant_packfile(cls, entry, pointer_size, globals())


class hkaSkeleton(hkReferencedObject):
    alignment = 16
    byte_size = 136
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 4274114267
    __version = 5

    local_members = (
        Member(16, "name", hkStringPtr, flags=32),
        Member(24, "parentIndices", hkArray(hkInt16), flags=32),
        Member(40, "bones", hkArray(hkaBone), flags=32),
        Member(56, "referencePose", hkArray(hkQsTransform), flags=32),
        Member(72, "referenceFloats", hkArray(hkReal), flags=32),
        Member(88, "floatSlots", hkArray(hkStringPtr), flags=32),
        Member(104, "localFrames", hkArray(hkaSkeletonLocalFrameOnBone), flags=32),
        Member(120, "partitions", hkArray(hkaSkeletonPartition), flags=32),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    parentIndices: list[hkInt16]
    bones: list[hkaBone]
    referencePose: list[hkQsTransform]
    referenceFloats: list[hkReal]
    floatSlots: list[hkStringPtr]
    localFrames: list[hkaSkeletonLocalFrameOnBone]
    partitions: list[hkaSkeletonPartition]


class hkaAnnotationTrack(hk):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "trackName", hkStringPtr, flags=32),
        Member(8, "annotations", hkArray(hkaAnnotationTrackAnnotation), flags=32),
    )
    members = local_members

    trackName: hkStringPtr
    annotations: list[hkaAnnotationTrackAnnotation]


class hkxVertexDescription(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "decls", hkArray(hkxVertexDescriptionElementDecl), flags=32),
    )
    members = local_members

    decls: list[hkxVertexDescriptionElementDecl]


class hkxAttributeGroup(hk):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "name", hkStringPtr, flags=32),
        Member(8, "attributes", hkArray(hkxAttribute), flags=32),
    )
    members = local_members

    name: hkStringPtr
    attributes: list[hkxAttribute]


class hknpConvexShape(hknpShape):
    alignment = 16
    byte_size = 48
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(40, "vertices", NewStruct(hkVector4), flags=0),
    )
    members = hknpShape.members + local_members

    vertices: tuple[hkVector4]


class hkpLimitedForceConstraintMotor(hkpConstraintMotor):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(16, "minForce", hkReal, flags=32),
        Member(20, "maxForce", hkReal, flags=32),
    )
    members = hkpConstraintMotor.members + local_members

    minForce: hkReal
    maxForce: hkReal


class hkpSetLocalTransformsConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 144
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(16, "transformA", hkTransform, flags=32),
        Member(80, "transformB", hkTransform, flags=32),
    )
    members = hkpConstraintAtom.members + local_members

    transformA: hkTransform
    transformB: hkTransform


class hknpPhysicsSystemData(hkReferencedObject):
    alignment = 16
    byte_size = 120
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(16, "materials", hkArray(hknpMaterial), flags=0),
        Member(32, "motionProperties", hkArray(hknpMotionProperties), flags=0),
        Member(48, "motionCinfos", hkArray(hknpMotionCinfo), flags=0),
        Member(64, "bodyCinfos", hkArray(hknpBodyCinfo), flags=0),
        Member(80, "constraintCinfos", hkArray(hknpConstraintCinfo), flags=0),
        Member(96, "referencedObjects", hkArray(Ptr(hkReferencedObject)), flags=0),
        Member(112, "name", hkStringPtr, flags=0),
    )
    members = hkReferencedObject.members + local_members

    materials: list[hknpMaterial]
    motionProperties: list[hknpMotionProperties]
    motionCinfos: list[hknpMotionCinfo]
    bodyCinfos: list[hknpBodyCinfo]
    constraintCinfos: list[hknpConstraintCinfo]
    referencedObjects: list[hkReferencedObject]
    name: hkStringPtr


class hknpMaterialLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(16, "materialAddedSignal", Ptr(_void), flags=1024),
        Member(24, "materialModifiedSignal", Ptr(_void), flags=1024),
        Member(32, "materialRemovedSignal", Ptr(_void), flags=1024),
        Member(
            40,
            "entries",
            hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations,
            flags=0,
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
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(16, "entryAddedSignal", Ptr(_void), flags=1024),
        Member(24, "entryModifiedSignal", Ptr(_void), flags=1024),
        Member(32, "entryRemovedSignal", Ptr(_void), flags=1024),
        Member(
            40,
            "entries",
            hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations,
            flags=0,
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
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(16, "qualityModifiedSignal", Ptr(_void), flags=1024),
        Member(32, "qualities", hkGenericStruct(hknpBodyQuality, 32), flags=256),
    )
    members = hkReferencedObject.members + local_members

    qualityModifiedSignal: _void
    qualities: tuple[hknpBodyQuality, ...]


class hkaSkeletonMapperData(hk):
    alignment = 16
    byte_size = 176
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 2

    local_members = (
        Member(0, "skeletonA", Ptr(hkaSkeleton), flags=32),
        Member(8, "skeletonB", Ptr(hkaSkeleton), flags=32),
        Member(16, "partitionMap", hkArray(hkInt16), flags=32),
        Member(
            32,
            "simpleMappingPartitionRanges",
            hkArray(hkaSkeletonMapperDataPartitionMappingRange),
            flags=32,
        ),
        Member(48, "chainMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange), flags=32),
        Member(64, "simpleMappings", hkArray(hkaSkeletonMapperDataSimpleMapping), flags=32),
        Member(80, "chainMappings", hkArray(hkaSkeletonMapperDataChainMapping), flags=32),
        Member(96, "unmappedBones", hkArray(hkInt16), flags=32),
        Member(112, "extractedMotionMapping", hkQsTransform, flags=32),
        Member(160, "keepUnmappedLocal", hkBool, flags=32),
        Member(164, "mappingType", hkEnum(hkaSkeletonMapperDataMappingType, hkInt32), flags=32),
    )
    members = local_members

    skeletonA: hkaSkeleton
    skeletonB: hkaSkeleton
    partitionMap: list[hkInt16]
    simpleMappingPartitionRanges: list[hkaSkeletonMapperDataPartitionMappingRange]
    chainMappingPartitionRanges: list[hkaSkeletonMapperDataPartitionMappingRange]
    simpleMappings: list[hkaSkeletonMapperDataSimpleMapping]
    chainMappings: list[hkaSkeletonMapperDataChainMapping]
    unmappedBones: list[hkInt16]
    extractedMotionMapping: hkQsTransform
    keepUnmappedLocal: hkBool
    mappingType: hkaSkeletonMapperDataMappingType


class hkRootLevelContainer(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 661831966

    local_members = (
        Member(0, "namedVariants", hkArray(hkRootLevelContainerNamedVariant), flags=32),
    )
    members = local_members

    namedVariants: list[hkRootLevelContainerNamedVariant]


class hkaAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 56
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 3

    local_members = (
        Member(12, "type", hkEnum(hkaAnimationAnimationType, hkInt32), flags=34),
        Member(16, "duration", hkReal, flags=32),
        Member(20, "numberOfTransformTracks", hkInt32, flags=32),
        Member(24, "numberOfFloatTracks", hkInt32, flags=32),
        Member(32, "extractedMotion", Ptr(hkaAnimatedReferenceFrame), flags=34),
        Member(40, "annotationTracks", hkArray(hkaAnnotationTrack), flags=32),
    )
    members = hkReferencedObject.members + local_members

    type: hkaAnimationAnimationType
    duration: hkReal
    numberOfTransformTracks: hkInt32
    numberOfFloatTracks: hkInt32
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]


class hkaAnimationBinding(hkReferencedObject):
    alignment = 16
    byte_size = 88
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 263164240
    __version = 3

    local_members = (
        Member(16, "originalSkeletonName", hkStringPtr, flags=32),
        Member(24, "animation", Ptr(hkaAnimation), flags=32),
        Member(32, "transformTrackToBoneIndices", hkArray(hkInt16), flags=32),
        Member(48, "floatTrackToFloatSlotIndices", hkArray(hkInt16), flags=32),
        Member(64, "partitionIndices", hkArray(hkInt16), flags=32),
        Member(80, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8), flags=32),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: hkStringPtr
    animation: hkaAnimation
    transformTrackToBoneIndices: list[hkInt16]
    floatTrackToFloatSlotIndices: list[hkInt16]
    partitionIndices: list[hkInt16]
    blendHint: hkaAnimationBindingBlendHint


class hkxVertexBuffer(hkReferencedObject):
    alignment = 16
    byte_size = 136
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(16, "data", hkxVertexBufferVertexData, flags=34),
        Member(120, "desc", hkxVertexDescription, flags=34),
    )
    members = hkReferencedObject.members + local_members

    data: hkxVertexBufferVertexData
    desc: hkxVertexDescription


class hkxAttributeHolder(hkReferencedObject):
    alignment = 16
    byte_size = 32
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 2

    local_members = (
        Member(16, "attributeGroups", hkArray(hkxAttributeGroup), flags=32),
    )
    members = hkReferencedObject.members + local_members

    attributeGroups: list[hkxAttributeGroup]


class hkxVertexAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 184
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(12, "time", hkReal, flags=32),
        Member(16, "vertData", hkxVertexBuffer, flags=32),
        Member(152, "vertexIndexMap", hkArray(hkInt32), flags=32),
        Member(168, "componentMap", hkArray(hkxVertexAnimationUsageMap), flags=32),
    )
    members = hkReferencedObject.members + local_members

    time: hkReal
    vertData: hkxVertexBuffer
    vertexIndexMap: list[hkInt32]
    componentMap: list[hkxVertexAnimationUsageMap]


class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 16
    byte_size = 48
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(32, "name", hkStringPtr, flags=32),
        Member(40, "className", hkStringPtr, flags=32),
    )
    members = hkxAttributeHolder.members + local_members

    name: hkStringPtr
    className: hkStringPtr


class hknpConvexPolytopeShape(hknpConvexShape):
    alignment = 16
    byte_size = 64
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 1021948899
    __version = 1

    local_members = (
        Member(44, "planes", NewStruct(hkVector4), flags=0),
        Member(48, "faces", NewStruct(hknpConvexPolytopeShapeFace), flags=0),
        Member(52, "indices", NewStruct(hkUint8), flags=0),
    )
    members = hknpConvexShape.members + local_members

    planes: tuple[hkVector4]
    faces: tuple[hknpConvexPolytopeShapeFace]
    indices: tuple[hkUint8]


class hknpCapsuleShape(hknpConvexPolytopeShape):
    alignment = 16
    byte_size = 96
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 1621581644

    local_members = (
        Member(64, "a", hkVector4, flags=0),
        Member(80, "b", hkVector4, flags=0),
    )
    members = hknpConvexPolytopeShape.members + local_members

    a: hkVector4
    b: hkVector4


class hkpPositionConstraintMotor(hkpLimitedForceConstraintMotor):
    alignment = 16
    byte_size = 40
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 339596288

    local_members = (
        Member(24, "tau", hkReal, flags=32),
        Member(28, "damping", hkReal, flags=32),
        Member(32, "proportionalRecoveryVelocity", hkReal, flags=32),
        Member(36, "constantRecoveryVelocity", hkReal, flags=32),
    )
    members = hkpLimitedForceConstraintMotor.members + local_members

    tau: hkReal
    damping: hkReal
    proportionalRecoveryVelocity: hkReal
    constantRecoveryVelocity: hkReal


class hkpRagdollConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 384
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom, flags=32),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom, flags=32),
        Member(160, "ragdollMotors", hkpRagdollMotorConstraintAtom, flags=32),
        Member(256, "angFriction", hkpAngFrictionConstraintAtom, flags=32),
        Member(272, "twistLimit", hkpTwistLimitConstraintAtom, flags=32),
        Member(304, "coneLimit", hkpConeLimitConstraintAtom, flags=32),
        Member(336, "planesLimit", hkpConeLimitConstraintAtom, flags=32),
        Member(368, "ballSocket", hkpBallSocketConstraintAtom, flags=32),
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
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 3700367531

    local_members = (
        Member(120, "skeleton", Ptr(hkaSkeleton), flags=0),
        Member(128, "boneToBodyMap", hkArray(hkInt32), flags=0),
    )
    members = hknpPhysicsSystemData.members + local_members

    skeleton: hkaSkeleton
    boneToBodyMap: list[hkInt32]


class hknpWorldCinfo(hk):
    alignment = 16
    byte_size = 256
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 5

    local_members = (
        Member(0, "bodyBufferCapacity", hkInt32, flags=0),
        Member(8, "userBodyBuffer", Ptr(_void), flags=1024),
        Member(16, "motionBufferCapacity", hkInt32, flags=0),
        Member(24, "userMotionBuffer", Ptr(_void), flags=1024),
        Member(32, "constraintBufferCapacity", hkInt32, flags=0),
        Member(40, "userConstraintBuffer", Ptr(_void), flags=1024),
        Member(48, "persistentStreamAllocator", Ptr(_void), flags=1024),
        Member(56, "materialLibrary", Ptr(hknpMaterialLibrary), flags=0),
        Member(64, "motionPropertiesLibrary", Ptr(hknpMotionPropertiesLibrary), flags=0),
        Member(72, "qualityLibrary", Ptr(hknpBodyQualityLibrary), flags=0),
        Member(80, "simulationType", hkEnum(hknpWorldCinfoSimulationType, hkUint8), flags=0),
        Member(84, "numSplitterCells", hkInt32, flags=0),
        Member(96, "gravity", hkVector4, flags=0),
        Member(112, "enableContactCaching", hkBool, flags=0),
        Member(113, "mergeEventsBeforeDispatch", hkBool, flags=0),
        Member(
            114,
            "leavingBroadPhaseBehavior",
            hkEnum(hknpWorldCinfoLeavingBroadPhaseBehavior, hkUint8),
            flags=0,
        ),
        Member(128, "broadPhaseAabb", hkAabb, flags=0),
        Member(160, "broadPhaseConfig", Ptr(hknpBroadPhaseConfig), flags=0),
        Member(168, "collisionFilter", Ptr(hknpCollisionFilter), flags=0),
        Member(176, "shapeTagCodec", Ptr(hknpShapeTagCodec), flags=0),
        Member(184, "collisionTolerance", hkReal, flags=0),
        Member(188, "relativeCollisionAccuracy", hkReal, flags=0),
        Member(192, "enableWeldingForDefaultObjects", hkBool, flags=0),
        Member(193, "enableWeldingForCriticalObjects", hkBool, flags=0),
        Member(196, "solverTau", hkReal, flags=0),
        Member(200, "solverDamp", hkReal, flags=0),
        Member(204, "solverIterations", hkInt32, flags=0),
        Member(208, "solverMicrosteps", hkInt32, flags=0),
        Member(212, "defaultSolverTimestep", hkReal, flags=0),
        Member(216, "maxApproachSpeedForHighQualitySolver", hkReal, flags=0),
        Member(220, "enableDeactivation", hkBool, flags=0),
        Member(221, "deleteCachesOnDeactivation", hkBool, flags=0),
        Member(224, "largeIslandSize", hkInt32, flags=0),
        Member(228, "enableSolverDynamicScheduling", hkBool, flags=0),
        Member(232, "contactSolverType", hkInt32, flags=0),
        Member(236, "unitScale", hkReal, flags=0),
        Member(240, "applyUnitScaleToStaticConstants", hkBool, flags=0),
    )
    members = local_members

    bodyBufferCapacity: hkInt32
    userBodyBuffer: _void
    motionBufferCapacity: hkInt32
    userMotionBuffer: _void
    constraintBufferCapacity: hkInt32
    userConstraintBuffer: _void
    persistentStreamAllocator: _void
    materialLibrary: hknpMaterialLibrary
    motionPropertiesLibrary: hknpMotionPropertiesLibrary
    qualityLibrary: hknpBodyQualityLibrary
    simulationType: hknpWorldCinfoSimulationType
    numSplitterCells: hkInt32
    gravity: hkVector4
    enableContactCaching: hkBool
    mergeEventsBeforeDispatch: hkBool
    leavingBroadPhaseBehavior: hknpWorldCinfoLeavingBroadPhaseBehavior
    broadPhaseAabb: hkAabb
    broadPhaseConfig: hknpBroadPhaseConfig
    collisionFilter: hknpCollisionFilter
    shapeTagCodec: hknpShapeTagCodec
    collisionTolerance: hkReal
    relativeCollisionAccuracy: hkReal
    enableWeldingForDefaultObjects: hkBool
    enableWeldingForCriticalObjects: hkBool
    solverTau: hkReal
    solverDamp: hkReal
    solverIterations: hkInt32
    solverMicrosteps: hkInt32
    defaultSolverTimestep: hkReal
    maxApproachSpeedForHighQualitySolver: hkReal
    enableDeactivation: hkBool
    deleteCachesOnDeactivation: hkBool
    largeIslandSize: hkInt32
    enableSolverDynamicScheduling: hkBool
    contactSolverType: hkInt32
    unitScale: hkReal
    applyUnitScaleToStaticConstants: hkBool


class hkaSkeletonMapper(hkReferencedObject):
    alignment = 16
    byte_size = 192
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 2900984988

    local_members = (
        Member(16, "mapping", hkaSkeletonMapperData, flags=32),
    )
    members = hkReferencedObject.members + local_members

    mapping: hkaSkeletonMapperData


class hkaSplineCompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 176
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 2352701310

    local_members = (
        Member(56, "numFrames", _int, flags=36),
        Member(60, "numBlocks", _int, flags=36),
        Member(64, "maxFramesPerBlock", _int, flags=36),
        Member(68, "maskAndQuantizationSize", _int, flags=36),
        Member(72, "blockDuration", hkReal, flags=36),
        Member(76, "blockInverseDuration", hkReal, flags=36),
        Member(80, "frameDuration", hkReal, flags=36),
        Member(88, "blockOffsets", hkArray(hkUint32), flags=36),
        Member(104, "floatBlockOffsets", hkArray(hkUint32), flags=36),
        Member(120, "transformOffsets", hkArray(hkUint32), flags=36),
        Member(136, "floatOffsets", hkArray(hkUint32), flags=36),
        Member(152, "data", hkArray(hkUint8), flags=36),
        Member(168, "endian", _int, flags=36),
    )
    members = hkaAnimation.members + local_members

    numFrames: _int
    numBlocks: _int
    maxFramesPerBlock: _int
    maskAndQuantizationSize: _int
    blockDuration: hkReal
    blockInverseDuration: hkReal
    frameDuration: hkReal
    blockOffsets: list[hkUint32]
    floatBlockOffsets: list[hkUint32]
    transformOffsets: list[hkUint32]
    floatOffsets: list[hkUint32]
    data: list[hkUint8]
    endian: _int


class hkaInterleavedUncompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 96
    tag_format_flags = 45
    tag_type_flags = 7

    __hsh = 3449291259
    __version = 1

    local_members = (
        Member(56, "transforms", hkArray(hkQsTransform), flags=32),
        Member(72, "floats", hkArray(hkReal), flags=32),
    )
    members = hkaAnimation.members + local_members

    transforms: list[hkQsTransform]
    floats: list[hkReal]


class hkaQuantizedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 96
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 213316226

    local_members = (
        Member(56, "data", hkArray(hkUint8), flags=36),
        Member(72, "endian", hkUint32, flags=36),
        Member(80, "skeleton", Ptr(hkReflectDetailOpaque), flags=37),
    )
    members = hkaAnimation.members + local_members

    data: list[hkUint8]
    endian: hkUint32
    skeleton: hkReflectDetailOpaque


class hkxMaterial(hkxAttributeHolder):
    alignment = 16
    byte_size = 224
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 5

    local_members = (
        Member(32, "name", hkStringPtr, flags=32),
        Member(40, "stages", hkArray(hkxMaterialTextureStage), flags=32),
        Member(64, "diffuseColor", hkVector4, flags=32),
        Member(80, "ambientColor", hkVector4, flags=32),
        Member(96, "specularColor", hkVector4, flags=32),
        Member(112, "emissiveColor", hkVector4, flags=32),
        Member(128, "subMaterials", hkArray(Ptr(DefType("hkxMaterial", lambda: hkxMaterial))), flags=32),
        Member(144, "extraData", Ptr(hkReferencedObject), flags=32),
        Member(152, "uvMapScale", hkGenericStruct(hkReal, 2), flags=32),
        Member(160, "uvMapOffset", hkGenericStruct(hkReal, 2), flags=32),
        Member(168, "uvMapRotation", hkReal, flags=32),
        Member(172, "uvMapAlgorithm", hkEnum(hkxMaterialUVMappingAlgorithm, hkUint32), flags=32),
        Member(176, "specularMultiplier", hkReal, flags=32),
        Member(180, "specularExponent", hkReal, flags=32),
        Member(184, "transparency", hkEnum(hkxMaterialTransparency, hkUint8), flags=32),
        Member(192, "userData", hkUlong, flags=32),
        Member(200, "properties", hkArray(hkxMaterialProperty), flags=34),
    )
    members = hkxAttributeHolder.members + local_members

    name: hkStringPtr
    stages: list[hkxMaterialTextureStage]
    diffuseColor: hkVector4
    ambientColor: hkVector4
    specularColor: hkVector4
    emissiveColor: hkVector4
    subMaterials: list[hkxMaterial]
    extraData: hkReferencedObject
    uvMapScale: tuple[hkReal, ...]
    uvMapOffset: tuple[hkReal, ...]
    uvMapRotation: hkReal
    uvMapAlgorithm: hkxMaterialUVMappingAlgorithm
    specularMultiplier: hkReal
    specularExponent: hkReal
    transparency: hkxMaterialTransparency
    userData: hkUlong
    properties: list[hkxMaterialProperty]


class hkpRagdollConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 416
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 3078430774

    local_members = (
        Member(32, "atoms", hkpRagdollConstraintDataAtoms, flags=32),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpRagdollConstraintDataAtoms


class hknpRefWorldCinfo(hkReferencedObject):
    alignment = 16
    byte_size = 272
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(16, "info", hknpWorldCinfo, flags=0),
    )
    members = hkReferencedObject.members + local_members

    info: hknpWorldCinfo


class hkxMeshSection(hkReferencedObject):
    alignment = 16
    byte_size = 112
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 5

    local_members = (
        Member(16, "vertexBuffer", Ptr(hkxVertexBuffer), flags=32),
        Member(24, "indexBuffers", hkArray(Ptr(hkxIndexBuffer)), flags=32),
        Member(40, "material", Ptr(hkxMaterial), flags=32),
        Member(48, "userChannels", hkArray(Ptr(hkReferencedObject)), flags=32),
        Member(64, "vertexAnimations", hkArray(Ptr(hkxVertexAnimation)), flags=32),
        Member(80, "linearKeyFrameHints", hkArray(hkReal), flags=32),
        Member(96, "boneMatrixMap", hkArray(hkMeshBoneIndexMapping), flags=32),
    )
    members = hkReferencedObject.members + local_members

    vertexBuffer: hkxVertexBuffer
    indexBuffers: list[hkxIndexBuffer]
    material: hkxMaterial
    userChannels: list[hkReferencedObject]
    vertexAnimations: list[hkxVertexAnimation]
    linearKeyFrameHints: list[hkReal]
    boneMatrixMap: list[hkMeshBoneIndexMapping]


class hknpPhysicsSceneData(hkReferencedObject):
    alignment = 16
    byte_size = 40
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 1880942380
    __version = 1

    local_members = (
        Member(16, "systemDatas", hkArray(Ptr(hknpPhysicsSystemData)), flags=0),
        Member(32, "worldCinfo", Ptr(hknpRefWorldCinfo), flags=0),
    )
    members = hkReferencedObject.members + local_members

    systemDatas: list[hknpPhysicsSystemData]
    worldCinfo: hknpRefWorldCinfo


class hkxMesh(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(16, "sections", hkArray(Ptr(hkxMeshSection)), flags=32),
        Member(32, "userChannelInfos", hkArray(Ptr(hkxMeshUserChannelInfo)), flags=32),
    )
    members = hkReferencedObject.members + local_members

    sections: list[hkxMeshSection]
    userChannelInfos: list[hkxMeshUserChannelInfo]


class hkaMeshBinding(hkReferencedObject):
    alignment = 16
    byte_size = 80
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 3

    local_members = (
        Member(16, "mesh", Ptr(hkxMesh), flags=32),
        Member(24, "originalSkeletonName", hkStringPtr, flags=32),
        Member(32, "name", hkStringPtr, flags=32),
        Member(40, "skeleton", Ptr(hkaSkeleton), flags=32),
        Member(48, "mappings", hkArray(hkaMeshBindingMapping), flags=32),
        Member(64, "boneFromSkinMeshTransforms", hkArray(hkTransform), flags=32),
    )
    members = hkReferencedObject.members + local_members

    mesh: hkxMesh
    originalSkeletonName: hkStringPtr
    name: hkStringPtr
    skeleton: hkaSkeleton
    mappings: list[hkaMeshBindingMapping]
    boneFromSkinMeshTransforms: list[hkTransform]


class hkaAnimationContainer(hkReferencedObject):
    alignment = 16
    byte_size = 96
    tag_format_flags = 41
    tag_type_flags = 7

    __hsh = 646291276
    __version = 1

    local_members = (
        Member(16, "skeletons", hkArray(hkRefPtr(hkaSkeleton)), flags=32),
        Member(32, "animations", hkArray(hkRefPtr(hkaAnimation)), flags=32),
        Member(48, "bindings", hkArray(hkRefPtr(hkaAnimationBinding)), flags=32),
        Member(64, "attachments", hkArray(hkRefPtr(hkaBoneAttachment)), flags=32),
        Member(80, "skins", hkArray(hkRefPtr(hkaMeshBinding)), flags=32),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]


class hkpLimitedForceConstraintMotor(hk):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flag = 7

    local_members = (
        Member(16, "minForce", hkReal, flags=0),
        Member(20, "maxForce", hkReal, flags=0),
    )


class hkp2dAngConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(2, "freeRotationAxis", hkUint8, flags=0),
        Member(3, "padding", hkStruct(hkUint8, 13), flags=0),
    )

    freeRotationAxis: hkUint8
    padding: tuple[hkUint8]


class hkpAngMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 40
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(2, "isEnabled", hkBool, flags=0),
        Member(3, "motorAxis", hkUint8, flags=0),
        Member(4, "initializedOffset", hkInt16, flags=0),
        Member(6, "previousTargetAngleOffset", hkInt16, flags=0),
        Member(8, "correspondingAngLimitSolverResultOffset", hkInt16, flags=0),
        Member(12, "targetAngle", hkReal, flags=0),
        Member(16, "motor", Ptr(hkpConstraintMotor), flags=0),
        Member(24, "padding", hkStruct(hkUint8, 20), flags=0),
    )


class hkpAngLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(2, "isEnabled", hkUint8, flags=0),
        Member(3, "limitAxis", hkUint8, flags=0),
        Member(4, "minAngle", hkReal, flags=0),
        Member(8, "maxAngle", hkReal, flags=0),
        Member(12, "angularLimitsTauFactor", hkReal, flags=0),
    )


class hkpLimitedHingeConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 272
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member(0, "transforms", hkpSetLocalTransformsConstraintAtom, flags=0),
        Member(144, "setupStabilization", hkpSetupStabilizationAtom, flags=0),
        Member(160, "angMotor", hkpAngMotorConstraintAtom, flags=0),
        Member(200, "angFriction", hkpAngFrictionConstraintAtom, flags=0),
        Member(216, "angLimit", hkpAngLimitConstraintAtom, flags=0),
        Member(232, "2dAng", hkp2dAngConstraintAtom, flags=0),
        Member(248, "ballSocket", hkpBallSocketConstraintAtom, flags=0),
    )


class hkpLimitedHingeConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 304
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(32, "atoms", hkpLimitedHingeConstraintDataAtoms, flags=256),
    )
