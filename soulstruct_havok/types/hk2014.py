"""Auto-generated types for Havok 2014."""
from __future__ import annotations
import typing as tp

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import TagDataType

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
        Member("vec", hkVector4f, offset=0, flags=32),
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
        Member("col0", hkVector4f, offset=0, flags=34),
        Member("col1", hkVector4f, offset=16, flags=34),
        Member("col2", hkVector4f, offset=32, flags=34),
        Member("col3", hkVector4f, offset=48, flags=34),
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
        Member("rotation", hkRotationf, offset=0, flags=34),
        Member("translation", hkVector4f, offset=48, flags=34),
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
        Member("translation", hkVector4f, offset=0, flags=32),
        Member("rotation", hkQuaternionf, offset=16, flags=32),
        Member("scale", hkVector4f, offset=32, flags=32),
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
        Member("memSizeAndRefCount", hkUint32, offset=8, flags=1024),
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
        Member("ptr", Ptr(hkReferencedObject), offset=0, flags=36),
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
        Member("frameType", hkInt8, offset=12, flags=33),
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
        Member("vectorData", hkArray(hkUint32), offset=0, flags=32),
        Member("floatData", hkArray(hkUint32), offset=16, flags=32),
        Member("uint32Data", hkArray(hkUint32), offset=32, flags=32),
        Member("uint16Data", hkArray(hkUint16), offset=48, flags=32),
        Member("uint8Data", hkArray(hkUint8), offset=64, flags=32),
        Member("numVerts", hkUint32, offset=80, flags=32),
        Member("vectorStride", hkUint32, offset=84, flags=32),
        Member("floatStride", hkUint32, offset=88, flags=32),
        Member("uint32Stride", hkUint32, offset=92, flags=32),
        Member("uint16Stride", hkUint32, offset=96, flags=32),
        Member("uint8Stride", hkUint32, offset=100, flags=32),
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
        Member("key", hkUint32, offset=0, flags=32),
        Member("value", hkUint32, offset=4, flags=32),
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
        Member("mapping", hkArray(hkInt16), offset=0, flags=32),
    )
    members = local_members

    mapping: list[hkInt16]


class hkaMeshBindingMapping(hk):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("mapping", hkArray(hkInt16), offset=0, flags=32),
    )
    members = local_members

    mapping: list[hkInt16]


class hkCompressedMassProperties(hk):
    alignment = 16
    byte_size = 32
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("centerOfMass", hkStruct(hkInt16, 4, TagDataType.IsVariable1), offset=0, flags=0),
        Member("inertia", hkStruct(hkInt16, 4, TagDataType.IsVariable1), offset=8, flags=0),
        Member("majorAxisSpace", hkStruct(hkInt16, 4, TagDataType.IsVariable1), offset=16, flags=0),
        Member("mass", hkReal, offset=24, flags=0),
        Member("volume", hkReal, offset=28, flags=0),
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
        Member("object", Ptr(hkReferencedObject), offset=0, flags=0),
        Member("key", hkUint16, offset=8, flags=0),
        Member("flags", hkUint16, offset=10, flags=0),
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
        Member("firstIndex", hkUint16, offset=0, flags=0),
        Member("numIndices", hkUint8, offset=2, flags=0),
        Member("minHalfAngle", hkUint8, offset=3, flags=0),
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
        Member("userData", hkUlong, offset=16, flags=32),
    )
    members = hkReferencedObject.members + local_members

    userData: hkUlong


class hkUFloat8(hk):
    alignment = 2
    byte_size = 1
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("value", hkUint8, offset=0, flags=32),
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
        Member("min", hkVector4, offset=0, flags=32),
        Member("max", hkVector4, offset=16, flags=32),
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
        Member("startMappingIndex", hkInt32, offset=0, flags=32),
        Member("numMappings", hkInt32, offset=4, flags=32),
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
        Member("boneA", hkInt16, offset=0, flags=32),
        Member("boneB", hkInt16, offset=2, flags=32),
        Member("aFromBTransform", hkQsTransform, offset=16, flags=32),
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
        Member("startBoneA", hkInt16, offset=0, flags=32),
        Member("endBoneA", hkInt16, offset=2, flags=32),
        Member("startBoneB", hkInt16, offset=4, flags=32),
        Member("endBoneB", hkInt16, offset=6, flags=32),
        Member("startAFromBTransform", hkQsTransform, offset=16, flags=32),
        Member("endAFromBTransform", hkQsTransform, offset=64, flags=32),
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
        Member("stringAndFlag", _const_char, offset=0, flags=36),
    )
    members = local_members

    stringAndFlag: _const_char


class hkBool(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 41
    tag_type_flags = 8194

    local_members = (
        Member("bool", _char, offset=0, flags=36),
    )
    members = local_members

    bool: _char


class hkHalf16(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 41
    tag_type_flags = 476677

    local_members = (
        Member("value", hkInt16, offset=0, flags=36),
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
        Member("up", hkVector4, offset=32, flags=32),
        Member("forward", hkVector4, offset=48, flags=32),
        Member("duration", hkReal, offset=64, flags=32),
        Member("referenceFrameSamples", hkArray(hkVector4), offset=72, flags=32),
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
        Member("name", hkStringPtr, offset=0, flags=32),
        Member("lockTranslation", hkBool, offset=8, flags=32),
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
        Member("localFrame", Ptr(hkLocalFrame), offset=0, flags=32),
        Member("boneIndex", hkInt16, offset=8, flags=32),
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
        Member("name", hkStringPtr, offset=0, flags=32),
        Member("startBoneIndex", hkInt16, offset=8, flags=32),
        Member("numBones", hkInt16, offset=10, flags=32),
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
        Member("time", hkReal, offset=0, flags=32),
        Member("text", hkStringPtr, offset=8, flags=32),
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
        Member("originalSkeletonName", hkStringPtr, offset=16, flags=32),
        Member("boneFromAttachment", hkMatrix4, offset=32, flags=32),
        Member("attachment", Ptr(hkReferencedObject), offset=96, flags=32),
        Member("name", hkStringPtr, offset=104, flags=32),
        Member("boneIndex", hkInt16, offset=112, flags=32),
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
        Member("byteOffset", hkUint32, offset=0, flags=32),
        Member("type", hkEnum(hkxVertexDescriptionElementDeclDataType, hkUint16), offset=4, flags=32),
        Member("usage", hkEnum(hkxVertexDescriptionElementDeclDataUsage, hkUint16), offset=6, flags=32),
        Member("byteStride", hkUint32, offset=8, flags=32),
        Member("numElements", hkUint8, offset=12, flags=32),
        Member("channelID", hkStringPtr, offset=16, flags=32),
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
        Member("indexType", hkEnum(hkxIndexBufferIndexType, hkInt8), offset=12, flags=32),
        Member("indices16", hkArray(hkUint16), offset=16, flags=32),
        Member("indices32", hkArray(hkUint32), offset=32, flags=32),
        Member("vertexBaseOffset", hkUint32, offset=48, flags=32),
        Member("length", hkUint32, offset=52, flags=32),
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
        Member("name", hkStringPtr, offset=0, flags=32),
        Member("value", Ptr(hkReferencedObject), offset=8, flags=32),
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
        Member("texture", Ptr(hkReferencedObject), offset=0, flags=32),
        Member("usageHint", hkEnum(hkxMaterialTextureStageTextureType, hkInt32), offset=8, flags=32),
        Member("tcoordChannel", hkInt32, offset=12, flags=32),
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
        Member("use", hkEnum(hkxVertexDescriptionElementDeclDataUsage, hkUint16), offset=0, flags=32),
        Member("useIndexOrig", hkUint8, offset=2, flags=32),
        Member("useIndexLocal", hkUint8, offset=3, flags=32),
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
        Member("compressedMassProperties", hkCompressedMassProperties, offset=16, flags=128),
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
        Member("entries", hkArray(hkRefCountedPropertiesEntry), offset=0, flags=0),
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
        Member("flags", hkEnum(hknpShapeFlagsEnum, hkUint16), offset=16, flags=256),
        Member("numShapeKeyBits", hkUint8, offset=18, flags=0),
        Member("dispatchType", hkEnum(hknpShapeEnum, hkUint8), offset=19, flags=0),
        Member("convexRadius", hkReal, offset=20, flags=0),
        Member("userData", hkUint64, offset=24, flags=0),
        Member("properties", Ptr(hkRefCountedProperties), offset=32, flags=0),
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
        Member("type", hkEnum(hkpConstraintMotorMotorType, hkInt8), offset=12, flags=32),
    )
    members = hkReferencedObject.members + local_members

    type: hkpConstraintMotorMotorType


class hkpConstraintAtom(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("type", hkEnum(hkpConstraintAtomAtomType, hkUint16), offset=0, flags=32),
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
        Member("enabled", hkBool, offset=2, flags=32),
        Member("padding", hkStruct(hkUint8, 1, TagDataType.IsVariable1), offset=3, flags=1024),
        Member("maxLinImpulse", hkReal, offset=4, flags=32),
        Member("maxAngImpulse", hkReal, offset=8, flags=32),
        Member("maxAngle", hkReal, offset=12, flags=32),
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
        Member("isEnabled", hkBool, offset=2, flags=32),
        Member("initializedOffset", hkInt16, offset=4, flags=33),
        Member("previousTargetAnglesOffset", hkInt16, offset=6, flags=33),
        Member("target_bRca", hkMatrix3, offset=16, flags=32),
        Member("motors", hkStruct(Ptr(hkpConstraintMotor), 3, TagDataType.IsVariable1), offset=64, flags=32),
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
        Member("isEnabled", hkUint8, offset=2, flags=32),
        Member("firstFrictionAxis", hkUint8, offset=3, flags=32),
        Member("numFrictionAxes", hkUint8, offset=4, flags=32),
        Member("maxFrictionTorque", hkReal, offset=8, flags=32),
        Member("padding", hkStruct(hkUint8, 4, TagDataType.IsVariable1), offset=12, flags=1024),
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
        Member("isEnabled", hkUint8, offset=2, flags=32),
        Member("twistAxis", hkUint8, offset=3, flags=32),
        Member("refAxis", hkUint8, offset=4, flags=32),
        Member("minAngle", hkReal, offset=8, flags=32),
        Member("maxAngle", hkReal, offset=12, flags=32),
        Member("angularLimitsTauFactor", hkReal, offset=16, flags=32),
        Member("padding", hkStruct(hkUint8, 12, TagDataType.IsVariable1), offset=20, flags=1024),
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
        Member("isEnabled", hkUint8, offset=2, flags=32),
        Member("twistAxisInA", hkUint8, offset=3, flags=32),
        Member("refAxisInB", hkUint8, offset=4, flags=32),
        Member("angleMeasurementMode", hkEnum(hkpConeLimitConstraintAtomMeasurementMode, hkUint8), offset=5, flags=32),
        Member("memOffsetToAngleOffset", hkUint8, offset=6, flags=32),
        Member("minAngle", hkReal, offset=8, flags=32),
        Member("maxAngle", hkReal, offset=12, flags=32),
        Member("angularLimitsTauFactor", hkReal, offset=16, flags=32),
        Member("padding", hkStruct(hkUint8, 12, TagDataType.IsVariable1), offset=20, flags=1024),
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
        Member("solvingMethod", hkEnum(hkpBallSocketConstraintAtomSolvingMethod, hkUint8), offset=2, flags=32),
        Member("bodiesToNotify", hkUint8, offset=3, flags=32),
        Member("velocityStabilizationFactor", hkUFloat8, offset=4, flags=34),
        Member("enableLinearImpulseLimit", hkBool, offset=5, flags=32),
        Member("breachImpulse", hkReal, offset=8, flags=32),
        Member("inertiaStabilizationFactor", hkReal, offset=12, flags=34),
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
        Member("name", hkStringPtr, offset=0, flags=256),
        Member("isExclusive", hkUint32, offset=8, flags=0),
        Member("flags", hkInt32, offset=12, flags=0),
        Member("triggerType", hkEnum(hknpMaterialTriggerType, hkUint8), offset=16, flags=0),
        Member("triggerManifoldTolerance", hkUFloat8, offset=17, flags=0),
        Member("dynamicFriction", hkHalf16, offset=18, flags=0),
        Member("staticFriction", hkHalf16, offset=20, flags=0),
        Member("restitution", hkHalf16, offset=22, flags=0),
        Member("frictionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8), offset=24, flags=0),
        Member("restitutionCombinePolicy", hkEnum(hknpMaterialCombinePolicy, hkUint8), offset=25, flags=0),
        Member("weldingTolerance", hkHalf16, offset=26, flags=0),
        Member("maxContactImpulse", hkReal, offset=28, flags=0),
        Member("fractionOfClippedImpulseToApply", hkReal, offset=32, flags=0),
        Member("massChangerCategory", hkEnum(hknpMaterialMassChangerCategory, hkUint8), offset=36, flags=0),
        Member("massChangerHeavyObjectFactor", hkHalf16, offset=38, flags=0),
        Member("softContactForceFactor", hkHalf16, offset=40, flags=0),
        Member("softContactDampFactor", hkHalf16, offset=42, flags=0),
        Member("softContactSeperationVelocity", hkUFloat8, offset=44, flags=0),
        Member("surfaceVelocity", Ptr(hknpSurfaceVelocity), offset=48, flags=0),
        Member("disablingCollisionsBetweenCvxCvxDynamicObjectsDistance", hkHalf16, offset=56, flags=0),
        Member("userData", hkUint64, offset=64, flags=128),
        Member("isShared", hkBool, offset=72, flags=0),
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
        Member("isExclusive", hkUint32, offset=0, flags=256),
        Member("flags", hkEnum(hknpMotionPropertiesFlagsEnum, hkUint32), offset=4, flags=0),
        Member("gravityFactor", hkReal, offset=8, flags=0),
        Member("timeFactor", hkReal, offset=12, flags=0),
        Member("maxLinearSpeed", hkReal, offset=16, flags=0),
        Member("maxAngularSpeed", hkReal, offset=20, flags=0),
        Member("linearDamping", hkReal, offset=24, flags=0),
        Member("angularDamping", hkReal, offset=28, flags=0),
        Member("solverStabilizationSpeedThreshold", hkReal, offset=32, flags=0),
        Member("solverStabilizationSpeedReduction", hkReal, offset=36, flags=0),
        Member("maxDistSqrd", hkReal, offset=40, flags=0),
        Member("maxRotSqrd", hkReal, offset=44, flags=0),
        Member("invBlockSize", hkReal, offset=48, flags=0),
        Member("pathingUpperThreshold", hkInt16, offset=52, flags=0),
        Member("pathingLowerThreshold", hkInt16, offset=54, flags=0),
        Member("numDeactivationFrequencyPasses", hkUint8, offset=56, flags=0),
        Member("deactivationVelocityScaleSquare", hkUint8, offset=57, flags=0),
        Member("minimumPathingVelocityScaleSquare", hkUint8, offset=58, flags=0),
        Member("spikingVelocityScaleThresholdSquared", hkUint8, offset=59, flags=0),
        Member("minimumSpikingVelocityScaleSquared", hkUint8, offset=60, flags=0),
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
        Member("motionPropertiesId", hkUint16, offset=0, flags=0),
        Member("enableDeactivation", hkBool, offset=2, flags=0),
        Member("inverseMass", hkReal, offset=4, flags=0),
        Member("massFactor", hkReal, offset=8, flags=0),
        Member("maxLinearAccelerationDistancePerStep", hkReal, offset=12, flags=0),
        Member("maxRotationToPreventTunneling", hkReal, offset=16, flags=0),
        Member("inverseInertiaLocal", hkVector4, offset=32, flags=0),
        Member("centerOfMassWorld", hkVector4, offset=48, flags=0),
        Member("orientation", hkQuaternionf, offset=64, flags=0),
        Member("linearVelocity", hkVector4, offset=80, flags=0),
        Member("angularVelocity", hkVector4, offset=96, flags=0),
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
        Member("shape", Ptr(hknpShape), offset=0, flags=512),
        Member("reservedBodyId", hkUint32, offset=8, flags=0),
        Member("motionId", hkUint32, offset=12, flags=0),
        Member("qualityId", hkUint8, offset=16, flags=0),
        Member("materialId", hkUint16, offset=18, flags=0),
        Member("collisionFilterInfo", hkUint32, offset=20, flags=0),
        Member("flags", hkInt32, offset=24, flags=0),
        Member("collisionLookAheadDistance", hkReal, offset=28, flags=0),
        Member("name", hkStringPtr, offset=32, flags=0),
        Member("userData", hkUint64, offset=40, flags=0),
        Member("position", hkVector4, offset=48, flags=0),
        Member("orientation", hkQuaternionf, offset=64, flags=0),
        Member("spuFlags", hkEnum(hknpBodyCinfoSpuFlagsEnum, hkUint8), offset=80, flags=0),
        Member("localFrame", Ptr(hkLocalFrame), offset=88, flags=0),
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
        Member("constraintData", Ptr(hkpConstraintData), offset=0, flags=0),
        Member("bodyA", hkUint32, offset=8, flags=0),
        Member("bodyB", hkUint32, offset=12, flags=0),
        Member("flags", hkEnum(hknpConstraintCinfoFlagsEnum, hkUint8), offset=16, flags=0),
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
        Member("elements", hkArray(hknpMaterial), offset=0, flags=0),
        Member("firstFree", hkInt32, offset=16, flags=0),
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
        Member("elements", hkArray(hknpMotionProperties), offset=0, flags=0),
        Member("firstFree", hkInt32, offset=16, flags=0),
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
        Member("priority", hkInt32, offset=0, flags=0),
        Member("supportedFlags", hkEnum(hknpBodyQualityFlagsEnum, hkUint32), offset=4, flags=0),
        Member("requestedFlags", hkEnum(hknpBodyQualityFlagsEnum, hkUint32), offset=8, flags=0),
        Member("contactCachingRelativeMovementThreshold", hkReal, offset=12, flags=0),
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
        Member("type", hkEnum(hknpCollisionFilterType, hkUint8), offset=12, flags=0),
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
        Member("type", hkEnum(hknpShapeTagCodecType, hkUint8), offset=12, flags=0),
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
        Member("name", hkStringPtr, offset=0, flags=36),
        Member("className", hkStringPtr, offset=8, flags=36),
        Member("variant", Ptr(hkReferencedObject), offset=16, flags=36),
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
        Member("name", hkStringPtr, offset=16, flags=32),
        Member("parentIndices", hkArray(hkInt16), offset=24, flags=32),
        Member("bones", hkArray(hkaBone), offset=40, flags=32),
        Member("referencePose", hkArray(hkQsTransform), offset=56, flags=32),
        Member("referenceFloats", hkArray(hkReal), offset=72, flags=32),
        Member("floatSlots", hkArray(hkStringPtr), offset=88, flags=32),
        Member("localFrames", hkArray(hkaSkeletonLocalFrameOnBone), offset=104, flags=32),
        Member("partitions", hkArray(hkaSkeletonPartition), offset=120, flags=32),
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
        Member("trackName", hkStringPtr, offset=0, flags=32),
        Member("annotations", hkArray(hkaAnnotationTrackAnnotation), offset=8, flags=32),
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
        Member("decls", hkArray(hkxVertexDescriptionElementDecl), offset=0, flags=32),
    )
    members = local_members

    decls: list[hkxVertexDescriptionElementDecl]


class hkxAttributeGroup(hk):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("name", hkStringPtr, offset=0, flags=32),
        Member("attributes", hkArray(hkxAttribute), offset=8, flags=32),
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
        Member("vertices", NewStruct(hkVector4), offset=40, flags=0),
    )
    members = hknpShape.members + local_members

    vertices: tuple[hkVector4]


class hkpLimitedForceConstraintMotor(hkpConstraintMotor):
    alignment = 16
    byte_size = 24
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("minForce", hkReal, offset=16, flags=32),
        Member("maxForce", hkReal, offset=20, flags=32),
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
        Member("transformA", hkTransform, offset=16, flags=32),
        Member("transformB", hkTransform, offset=80, flags=32),
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
        Member("materials", hkArray(hknpMaterial), offset=16, flags=0),
        Member("motionProperties", hkArray(hknpMotionProperties), offset=32, flags=0),
        Member("motionCinfos", hkArray(hknpMotionCinfo), offset=48, flags=0),
        Member("bodyCinfos", hkArray(hknpBodyCinfo), offset=64, flags=0),
        Member("constraintCinfos", hkArray(hknpConstraintCinfo), offset=80, flags=0),
        Member("referencedObjects", hkArray(Ptr(hkReferencedObject)), offset=96, flags=0),
        Member("name", hkStringPtr, offset=112, flags=0),
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
        Member("materialAddedSignal", Ptr(_void), offset=16, flags=1024),
        Member("materialModifiedSignal", Ptr(_void), offset=24, flags=1024),
        Member("materialRemovedSignal", Ptr(_void), offset=32, flags=1024),
        Member("entries", hkFreeListArrayhknpMaterialhknpMaterialId8hknpMaterialFreeListArrayOperations, offset=40, flags=0),
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
        Member("entryAddedSignal", Ptr(_void), offset=16, flags=1024),
        Member("entryModifiedSignal", Ptr(_void), offset=24, flags=1024),
        Member("entryRemovedSignal", Ptr(_void), offset=32, flags=1024),
        Member("entries", hkFreeListArrayhknpMotionPropertieshknpMotionPropertiesId8hknpMotionPropertiesFreeListArrayOperations, offset=40, flags=0),
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
        Member("qualityModifiedSignal", Ptr(_void), offset=16, flags=1024),
        Member("qualities", hkStruct(hknpBodyQuality, 32, TagDataType.IsVariable1), offset=32, flags=256),
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
        Member("skeletonA", Ptr(hkaSkeleton), offset=0, flags=32),
        Member("skeletonB", Ptr(hkaSkeleton), offset=8, flags=32),
        Member("partitionMap", hkArray(hkInt16), offset=16, flags=32),
        Member("simpleMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange), offset=32, flags=32),
        Member("chainMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange), offset=48, flags=32),
        Member("simpleMappings", hkArray(hkaSkeletonMapperDataSimpleMapping), offset=64, flags=32),
        Member("chainMappings", hkArray(hkaSkeletonMapperDataChainMapping), offset=80, flags=32),
        Member("unmappedBones", hkArray(hkInt16), offset=96, flags=32),
        Member("extractedMotionMapping", hkQsTransform, offset=112, flags=32),
        Member("keepUnmappedLocal", hkBool, offset=160, flags=32),
        Member("mappingType", hkEnum(hkaSkeletonMapperDataMappingType, hkInt32), offset=164, flags=32),
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
        Member("namedVariants", hkArray(hkRootLevelContainerNamedVariant), offset=0, flags=32),
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
        Member("type", hkEnum(hkaAnimationAnimationType, hkInt32), offset=12, flags=34),
        Member("duration", hkReal, offset=16, flags=32),
        Member("numberOfTransformTracks", hkInt32, offset=20, flags=32),
        Member("numberOfFloatTracks", hkInt32, offset=24, flags=32),
        Member("extractedMotion", Ptr(hkaAnimatedReferenceFrame), offset=32, flags=34),
        Member("annotationTracks", hkArray(hkaAnnotationTrack), offset=40, flags=32),
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
        Member("originalSkeletonName", hkStringPtr, offset=16, flags=32),
        Member("animation", Ptr(hkaAnimation), offset=24, flags=32),
        Member("transformTrackToBoneIndices", hkArray(hkInt16), offset=32, flags=32),
        Member("floatTrackToFloatSlotIndices", hkArray(hkInt16), offset=48, flags=32),
        Member("partitionIndices", hkArray(hkInt16), offset=64, flags=32),
        Member("blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8), offset=80, flags=32),
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
        Member("data", hkxVertexBufferVertexData, offset=16, flags=34),
        Member("desc", hkxVertexDescription, offset=120, flags=34),
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
        Member("attributeGroups", hkArray(hkxAttributeGroup), offset=16, flags=32),
    )
    members = hkReferencedObject.members + local_members

    attributeGroups: list[hkxAttributeGroup]


class hkxVertexAnimation(hkReferencedObject):
    alignment = 16
    byte_size = 184
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("time", hkReal, offset=12, flags=32),
        Member("vertData", hkxVertexBuffer, offset=16, flags=32),
        Member("vertexIndexMap", hkArray(hkInt32), offset=152, flags=32),
        Member("componentMap", hkArray(hkxVertexAnimationUsageMap), offset=168, flags=32),
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
        Member("name", hkStringPtr, offset=32, flags=32),
        Member("className", hkStringPtr, offset=40, flags=32),
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
        Member("planes", NewStruct(hkVector4), offset=44, flags=0),
        Member("faces", NewStruct(hknpConvexPolytopeShapeFace), offset=48, flags=0),
        Member("indices", NewStruct(hkUint8), offset=52, flags=0),
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
        Member("a", hkVector4, offset=64, flags=0),
        Member("b", hkVector4, offset=80, flags=0),
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
        Member("tau", hkReal, offset=24, flags=32),
        Member("damping", hkReal, offset=28, flags=32),
        Member("proportionalRecoveryVelocity", hkReal, offset=32, flags=32),
        Member("constantRecoveryVelocity", hkReal, offset=36, flags=32),
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
        Member("transforms", hkpSetLocalTransformsConstraintAtom, offset=0, flags=32),
        Member("setupStabilization", hkpSetupStabilizationAtom, offset=144, flags=32),
        Member("ragdollMotors", hkpRagdollMotorConstraintAtom, offset=160, flags=32),
        Member("angFriction", hkpAngFrictionConstraintAtom, offset=256, flags=32),
        Member("twistLimit", hkpTwistLimitConstraintAtom, offset=272, flags=32),
        Member("coneLimit", hkpConeLimitConstraintAtom, offset=304, flags=32),
        Member("planesLimit", hkpConeLimitConstraintAtom, offset=336, flags=32),
        Member("ballSocket", hkpBallSocketConstraintAtom, offset=368, flags=32),
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
        Member("skeleton", Ptr(hkaSkeleton), offset=120, flags=0),
        Member("boneToBodyMap", hkArray(hkInt32), offset=128, flags=0),
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
        Member("bodyBufferCapacity", hkInt32, offset=0, flags=0),
        Member("userBodyBuffer", Ptr(_void), offset=8, flags=1024),
        Member("motionBufferCapacity", hkInt32, offset=16, flags=0),
        Member("userMotionBuffer", Ptr(_void), offset=24, flags=1024),
        Member("constraintBufferCapacity", hkInt32, offset=32, flags=0),
        Member("userConstraintBuffer", Ptr(_void), offset=40, flags=1024),
        Member("persistentStreamAllocator", Ptr(_void), offset=48, flags=1024),
        Member("materialLibrary", Ptr(hknpMaterialLibrary), offset=56, flags=0),
        Member("motionPropertiesLibrary", Ptr(hknpMotionPropertiesLibrary), offset=64, flags=0),
        Member("qualityLibrary", Ptr(hknpBodyQualityLibrary), offset=72, flags=0),
        Member("simulationType", hkEnum(hknpWorldCinfoSimulationType, hkUint8), offset=80, flags=0),
        Member("numSplitterCells", hkInt32, offset=84, flags=0),
        Member("gravity", hkVector4, offset=96, flags=0),
        Member("enableContactCaching", hkBool, offset=112, flags=0),
        Member("mergeEventsBeforeDispatch", hkBool, offset=113, flags=0),
        Member("leavingBroadPhaseBehavior", hkEnum(hknpWorldCinfoLeavingBroadPhaseBehavior, hkUint8), offset=114, flags=0),
        Member("broadPhaseAabb", hkAabb, offset=128, flags=0),
        Member("broadPhaseConfig", Ptr(hknpBroadPhaseConfig), offset=160, flags=0),
        Member("collisionFilter", Ptr(hknpCollisionFilter), offset=168, flags=0),
        Member("shapeTagCodec", Ptr(hknpShapeTagCodec), offset=176, flags=0),
        Member("collisionTolerance", hkReal, offset=184, flags=0),
        Member("relativeCollisionAccuracy", hkReal, offset=188, flags=0),
        Member("enableWeldingForDefaultObjects", hkBool, offset=192, flags=0),
        Member("enableWeldingForCriticalObjects", hkBool, offset=193, flags=0),
        Member("solverTau", hkReal, offset=196, flags=0),
        Member("solverDamp", hkReal, offset=200, flags=0),
        Member("solverIterations", hkInt32, offset=204, flags=0),
        Member("solverMicrosteps", hkInt32, offset=208, flags=0),
        Member("defaultSolverTimestep", hkReal, offset=212, flags=0),
        Member("maxApproachSpeedForHighQualitySolver", hkReal, offset=216, flags=0),
        Member("enableDeactivation", hkBool, offset=220, flags=0),
        Member("deleteCachesOnDeactivation", hkBool, offset=221, flags=0),
        Member("largeIslandSize", hkInt32, offset=224, flags=0),
        Member("enableSolverDynamicScheduling", hkBool, offset=228, flags=0),
        Member("contactSolverType", hkInt32, offset=232, flags=0),
        Member("unitScale", hkReal, offset=236, flags=0),
        Member("applyUnitScaleToStaticConstants", hkBool, offset=240, flags=0),
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
        Member("mapping", hkaSkeletonMapperData, offset=16, flags=32),
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
        Member("numFrames", _int, offset=56, flags=36),
        Member("numBlocks", _int, offset=60, flags=36),
        Member("maxFramesPerBlock", _int, offset=64, flags=36),
        Member("maskAndQuantizationSize", _int, offset=68, flags=36),
        Member("blockDuration", hkReal, offset=72, flags=36),
        Member("blockInverseDuration", hkReal, offset=76, flags=36),
        Member("frameDuration", hkReal, offset=80, flags=36),
        Member("blockOffsets", hkArray(hkUint32), offset=88, flags=36),
        Member("floatBlockOffsets", hkArray(hkUint32), offset=104, flags=36),
        Member("transformOffsets", hkArray(hkUint32), offset=120, flags=36),
        Member("floatOffsets", hkArray(hkUint32), offset=136, flags=36),
        Member("data", hkArray(hkUint8), offset=152, flags=36),
        Member("endian", _int, offset=168, flags=36),
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
        Member("transforms", hkArray(hkQsTransform), offset=56, flags=32),
        Member("floats", hkArray(hkReal), offset=72, flags=32),
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
        Member("data", hkArray(hkUint8), offset=56, flags=36),
        Member("endian", hkUint32, offset=72, flags=36),
        Member("skeleton", Ptr(hkReflectDetailOpaque), offset=80, flags=37),
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
        Member("name", hkStringPtr, offset=32, flags=32),
        Member("stages", hkArray(hkxMaterialTextureStage), offset=40, flags=32),
        Member("diffuseColor", hkVector4, offset=64, flags=32),
        Member("ambientColor", hkVector4, offset=80, flags=32),
        Member("specularColor", hkVector4, offset=96, flags=32),
        Member("emissiveColor", hkVector4, offset=112, flags=32),
        Member("subMaterials", hkArray(Ptr(DefType("hkxMaterial", lambda: hkxMaterial))), offset=128, flags=32),
        Member("extraData", Ptr(hkReferencedObject), offset=144, flags=32),
        Member("uvMapScale", hkStruct(hkReal, 2, TagDataType.IsVariable1), offset=152, flags=32),
        Member("uvMapOffset", hkStruct(hkReal, 2, TagDataType.IsVariable1), offset=160, flags=32),
        Member("uvMapRotation", hkReal, offset=168, flags=32),
        Member("uvMapAlgorithm", hkEnum(hkxMaterialUVMappingAlgorithm, hkUint32), offset=172, flags=32),
        Member("specularMultiplier", hkReal, offset=176, flags=32),
        Member("specularExponent", hkReal, offset=180, flags=32),
        Member("transparency", hkEnum(hkxMaterialTransparency, hkUint8), offset=184, flags=32),
        Member("userData", hkUlong, offset=192, flags=32),
        Member("properties", hkArray(hkxMaterialProperty), offset=200, flags=34),
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
        Member("atoms", hkpRagdollConstraintDataAtoms, offset=32, flags=32),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpRagdollConstraintDataAtoms


class hknpRefWorldCinfo(hkReferencedObject):
    alignment = 16
    byte_size = 272
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("info", hknpWorldCinfo, offset=16, flags=0),
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
        Member("vertexBuffer", Ptr(hkxVertexBuffer), offset=16, flags=32),
        Member("indexBuffers", hkArray(Ptr(hkxIndexBuffer)), offset=24, flags=32),
        Member("material", Ptr(hkxMaterial), offset=40, flags=32),
        Member("userChannels", hkArray(Ptr(hkReferencedObject)), offset=48, flags=32),
        Member("vertexAnimations", hkArray(Ptr(hkxVertexAnimation)), offset=64, flags=32),
        Member("linearKeyFrameHints", hkArray(hkReal), offset=80, flags=32),
        Member("boneMatrixMap", hkArray(hkMeshBoneIndexMapping), offset=96, flags=32),
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
        Member("systemDatas", hkArray(Ptr(hknpPhysicsSystemData)), offset=16, flags=0),
        Member("worldCinfo", Ptr(hknpRefWorldCinfo), offset=32, flags=0),
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
        Member("sections", hkArray(Ptr(hkxMeshSection)), offset=16, flags=32),
        Member("userChannelInfos", hkArray(Ptr(hkxMeshUserChannelInfo)), offset=32, flags=32),
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
        Member("mesh", Ptr(hkxMesh), offset=16, flags=32),
        Member("originalSkeletonName", hkStringPtr, offset=24, flags=32),
        Member("name", hkStringPtr, offset=32, flags=32),
        Member("skeleton", Ptr(hkaSkeleton), offset=40, flags=32),
        Member("mappings", hkArray(hkaMeshBindingMapping), offset=48, flags=32),
        Member("boneFromSkinMeshTransforms", hkArray(hkTransform), offset=64, flags=32),
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
        Member("skeletons", hkArray(hkRefPtr(hkaSkeleton)), offset=16, flags=32),
        Member("animations", hkArray(hkRefPtr(hkaAnimation)), offset=32, flags=32),
        Member("bindings", hkArray(hkRefPtr(hkaAnimationBinding)), offset=48, flags=32),
        Member("attachments", hkArray(hkRefPtr(hkaBoneAttachment)), offset=64, flags=32),
        Member("skins", hkArray(hkRefPtr(hkaMeshBinding)), offset=80, flags=32),
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
        Member("minForce", hkReal, offset=16, flags=0),
        Member("maxForce", hkReal, offset=20, flags=0),
    )


class hkp2dAngConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("freeRotationAxis", hkUint8, offset=2, flags=0),
        Member("padding", hkStruct(hkUint8, 13), offset=3, flags=0),
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
        Member("isEnabled", hkBool, offset=2, flags=0),
        Member("motorAxis", hkUint8, offset=3, flags=0),
        Member("initializedOffset", hkInt16, offset=4, flags=0),
        Member("previousTargetAngleOffset", hkInt16, offset=6, flags=0),
        Member("correspondingAngLimitSolverResultOffset", hkInt16, offset=8, flags=0),
        Member("targetAngle", hkReal, offset=12, flags=0),
        Member("motor", Ptr(hkpConstraintMotor), offset=16, flags=0),
        Member("padding", hkStruct(hkUint8, 20), offset=24, flags=0),
    )


class hkpAngLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("isEnabled", hkUint8, offset=2, flags=0),
        Member("limitAxis", hkUint8, offset=3, flags=0),
        Member("minAngle", hkReal, offset=4, flags=0),
        Member("maxAngle", hkReal, offset=8, flags=0),
        Member("angularLimitsTauFactor", hkReal, offset=12, flags=0),
    )


class hkpLimitedHingeConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 272
    tag_format_flags = 41
    tag_type_flags = 7

    __version = 1

    local_members = (
        Member("transforms", hkpSetLocalTransformsConstraintAtom, offset=0, flags=0),
        Member("setupStabilization", hkpSetupStabilizationAtom, offset=144, flags=0),
        Member("angMotor", hkpAngMotorConstraintAtom, offset=160, flags=0),
        Member("angFriction", hkpAngFrictionConstraintAtom, offset=200, flags=0),
        Member("angLimit", hkpAngLimitConstraintAtom, offset=216, flags=0),
        Member("2dAng", hkp2dAngConstraintAtom, offset=232, flags=0),
        Member("ballSocket", hkpBallSocketConstraintAtom, offset=248, flags=0),
    )


class hkpLimitedHingeConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 304
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member("atoms", hkpLimitedHingeConstraintDataAtoms, offset=32, flags=256),
    )
