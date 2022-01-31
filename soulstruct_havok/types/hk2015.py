"""Auto-generated types for Havok 2015.

Generated from files:
    Skeleton.HKX
    c2240.hkx
    a00_3000.hkx
"""
from __future__ import annotations

from soulstruct_havok.enums import TagDataType, MemberFlags
from soulstruct_havok.types.core import *


# --- Invalid Types --- #


class hkReflectDetailOpaque(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = TagDataType.Invalid

    __tag_format_flags = 9
    __real_name = "hkReflect::Detail::Opaque"
    local_members = ()


# --- Primitive Types --- #


class _int(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "int"
    local_members = ()


class _const_charSTAR(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.CharArray

    __tag_format_flags = 9
    __real_name = "const char*"
    local_members = ()


class _unsigned_short(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16

    __tag_format_flags = 9
    __real_name = "unsigned short"
    local_members = ()


class _char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8

    __tag_format_flags = 9
    __hsh = 4184862313
    __real_name = "char"
    local_members = ()


class _float(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Float | TagDataType.Float32

    __tag_format_flags = 9
    __real_name = "float"
    local_members = ()


class _short(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int16

    __tag_format_flags = 9
    __real_name = "short"
    local_members = ()


class _signed_char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8

    __tag_format_flags = 9
    __real_name = "signed char"
    local_members = ()


class _unsigned_long_long(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Int | TagDataType.Int64

    __tag_format_flags = 9
    __real_name = "unsigned long long"
    local_members = ()


class _unsigned_int(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "unsigned int"
    local_members = ()


class _unsigned_char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8

    __tag_format_flags = 9
    __real_name = "unsigned char"
    local_members = ()


class _void(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = TagDataType.Void

    __tag_format_flags = 25
    __abstract_value = 1
    __real_name = "void"
    local_members = ()


# --- Havok Struct Types --- #


class hkVector4f(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Struct | 4 << 8

    __tag_format_flags = 11
    local_members = ()


class hkQuaternionf(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Struct | 4 << 8

    __tag_format_flags = 43

    local_members = (
        Member(0, "vec", hkVector4f),
    )
    members = local_members

    vec: hkVector4f


class hkRotationImpl(hkStruct(_float, 12)):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Struct | 12 << 8

    __tag_format_flags = 11
    local_members = ()

    __templates = (
        TemplateType("tFT", type=_float),
    )


class hkVector4(hkVector4f):
    """Havok alias."""
    __tag_format_flags = 0
    __hsh = 3266831369
    local_members = ()


class hkMatrix3Impl(hkStruct(_float, 12)):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Struct | 12 << 8

    __tag_format_flags = 11
    local_members = ()

    __templates = (
        TemplateType("tFT", type=_float),
    )


class hkMatrix4f(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Struct | 16 << 8

    __tag_format_flags = 43

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
    __tag_format_flags = 0
    local_members = ()


class hkMatrix3f(hkMatrix3Impl):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkMatrix4(hkMatrix4f):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkTransformf(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Struct | 16 << 8

    __tag_format_flags = 43

    local_members = (
        Member(0, "rotation", hkRotationf, MemberFlags.Protected),
        Member(48, "translation", hkVector4f, MemberFlags.Protected),
    )
    members = local_members

    rotation: hkRotationf
    translation: hkVector4f


class hkMatrix3(hkMatrix3f):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkTransform(hkTransformf):
    """Havok alias."""
    __tag_format_flags = 0
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
    __tag_format_flags = 0
    local_members = ()


class hkUint32(_unsigned_int):
    """Havok alias."""
    __tag_format_flags = 0
    __hsh = 1716249908
    local_members = ()


# --- Havok Wrappers --- #


class hkUint16(_unsigned_short):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkReal(_float):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkInt16(_short):
    """Havok alias."""
    __tag_format_flags = 0
    __hsh = 1556469994
    local_members = ()


class hkInt32(_int):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkInt8(_signed_char):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkUlong(_unsigned_long_long):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkUint8(_unsigned_char):
    """Havok alias."""
    __tag_format_flags = 0
    __hsh = 3721671547
    local_members = ()


class hkUint64(_unsigned_long_long):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


# --- Havok Core Types --- #


class hkBaseObject(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 144
    local_members = ()


class hkContainerHeapAllocator(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 16
    local_members = ()


class hkStringPtr(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.CharArray

    __tag_format_flags = 41
    __hsh = 2837000324

    local_members = (
        Member(0, "stringAndFlag", _const_charSTAR, MemberFlags.Private),
    )
    members = local_members

    stringAndFlag: str


class hkReferencedObject(hkBaseObject):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "memSizeAndFlags", hkUint16, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(10, "refCount", hkUint16, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkBaseObject.members + local_members

    memSizeAndFlags: int
    refCount: int


class hkaBoneAttachment(hkReferencedObject):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(16, "originalSkeletonName", hkStringPtr),
        Member(32, "boneFromAttachment", hkMatrix4),
        Member(96, "attachment", hkRefVariant(hkReferencedObject, hsh=2872857893)),
        Member(104, "name", hkStringPtr),
        Member(112, "boneIndex", hkInt16),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    boneFromAttachment: hkMatrix4
    attachment: hkReferencedObject
    name: str
    boneIndex: int


class hkaSkeletonPartition(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkaSkeleton::Partition"

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "startBoneIndex", hkInt16),
        Member(10, "numBones", hkInt16),
    )
    members = local_members

    name: str
    startBoneIndex: int
    numBones: int


class hkaAnimationAnimationType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkaAnimation::AnimationType"
    local_members = ()


class hkaAnimationBindingBlendHint(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkaAnimationBinding::BlendHint"
    local_members = ()


class hkaMeshBindingMapping(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkaMeshBinding::Mapping"

    local_members = (
        Member(0, "mapping", hkArray(hkInt16, hsh=2354433887)),
    )
    members = local_members

    mapping: list[int]


class hkBool(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Bool | TagDataType.Int8

    __tag_format_flags = 41

    local_members = (
        Member(0, "bool", _char, MemberFlags.Private),
    )
    members = local_members

    bool: int


class hkLocalFrame(hkReferencedObject):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3
    local_members = ()


class hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkaAnimatedReferenceFrame::hkaReferenceFrameTypeEnum"
    local_members = ()


class hkaAnnotationTrackAnnotation(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkaAnnotationTrack::Annotation"

    local_members = (
        Member(0, "time", hkReal),
        Member(8, "text", hkStringPtr),
    )
    members = local_members

    time: float
    text: str


class hkMeshBoneIndexMapping(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "mapping", hkArray(hkInt16, hsh=2354433887)),
    )
    members = local_members

    mapping: list[int]


class hkxVertexBufferVertexData(hk):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2
    __real_name = "hkxVertexBuffer::VertexData"

    local_members = (
        Member(0, "vectorData", hkArray(_unsigned_int)),
        Member(16, "floatData", hkArray(_unsigned_int)),
        Member(32, "uint32Data", hkArray(hkUint32, hsh=4255738572)),
        Member(48, "uint16Data", hkArray(hkUint16)),
        Member(64, "uint8Data", hkArray(hkUint8, hsh=2877151166)),
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


class hkxMaterialUVMappingAlgorithm(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkxMaterial::UVMappingAlgorithm"
    local_members = ()


class hkxMaterialTransparency(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkxMaterial::Transparency"
    local_members = ()


class hkxMaterialProperty(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkxMaterial::Property"

    local_members = (
        Member(0, "key", hkUint32),
        Member(4, "value", hkUint32),
    )
    members = local_members

    key: int
    value: int


class hkxIndexBufferIndexType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkxIndexBuffer::IndexType"
    local_members = ()


class hkxAttribute(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "value", hkRefVariant(hkReferencedObject, hsh=2872857893)),
    )
    members = local_members

    name: str
    value: hkReferencedObject


class hkxMaterialTextureType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkxMaterial::TextureType"
    local_members = ()


class hkxVertexDescriptionDataType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkxVertexDescription::DataType"
    local_members = ()


class hkxVertexDescriptionDataUsage(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkxVertexDescription::DataUsage"
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


class hkpWorldCinfoBroadPhaseType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpWorldCinfo::BroadPhaseType"
    local_members = ()


class hkpWorldCinfoBroadPhaseBorderBehaviour(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpWorldCinfo::BroadPhaseBorderBehaviour"
    local_members = ()


class hkpConvexListFilter(hkReferencedObject):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3
    local_members = ()


class hkWorldMemoryAvailableWatchDog(hkReferencedObject):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1
    local_members = ()


class hkpWorldCinfoContactPointGeneration(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpWorldCinfo::ContactPointGeneration"
    local_members = ()


class hkpWorldCinfoSimulationType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpWorldCinfo::SimulationType"
    local_members = ()


class hkpCollidableCollidableFilter(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 147
    local_members = ()


class hkpShapeCollectionFilter(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 147
    local_members = ()


class hkpRayShapeCollectionFilter(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 147
    local_members = ()


class hkpRayCollidableFilter(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 147
    local_members = ()


class hkpCollisionFilterhkpFilterType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpCollisionFilter::hkpFilterType"
    local_members = ()


class hkpAction(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(16, "world", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
        Member(24, "island", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
        Member(32, "userData", hkUlong, MemberFlags.Protected),
        Member(40, "name", hkStringPtr, MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    world: hkReflectDetailOpaque
    island: hkReflectDetailOpaque
    userData: int
    name: str


class hkpConstraintInstanceSmallArraySerializeOverrideType(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpConstraintInstance::SmallArraySerializeOverrideType"

    local_members = (
        Member(0, "data", Ptr(_void), MemberFlags.NotSerializable),
        Member(8, "size", hkUint16),
        Member(10, "capacityAndFlags", hkUint16),
    )
    members = local_members

    data: _void
    size: int
    capacityAndFlags: int


class hkpEntitySmallArraySerializeOverrideType(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpEntity::SmallArraySerializeOverrideType"

    local_members = (
        Member(0, "data", Ptr(_void), MemberFlags.NotSerializable),
        Member(8, "size", hkUint16),
        Member(10, "capacityAndFlags", hkUint16),
    )
    members = local_members

    data: _void
    size: int
    capacityAndFlags: int


class hkpEntitySpuCollisionCallback(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkpEntity::SpuCollisionCallback"

    local_members = (
        Member(0, "util", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(8, "capacity", hkUint16, MemberFlags.NotSerializable),
        Member(10, "eventFilter", hkUint8),
        Member(11, "userFilter", hkUint8),
    )
    members = local_members

    util: hkReflectDetailOpaque
    capacity: int
    eventFilter: int
    userFilter: int


class hkpConstraintData(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(16, "userData", hkUlong),
    )
    members = hkReferencedObject.members + local_members

    userData: int


class hkpConstraintInstanceConstraintPriority(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpConstraintInstance::ConstraintPriority"
    local_members = ()


class hkpConstraintInstanceOnDestructionRemapInfo(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpConstraintInstance::OnDestructionRemapInfo"
    local_members = ()


class hkMultiThreadCheck(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "threadId", hkUint32, MemberFlags.NotSerializable),
        Member(4, "stackTraceId", _int, MemberFlags.NotSerializable),
        Member(8, "markCount", hkUint16, MemberFlags.NotSerializable),
        Member(10, "markBitStack", hkUint16, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = local_members

    threadId: int
    stackTraceId: int
    markCount: int
    markBitStack: int


class hkHalf16(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Float | TagDataType.Float16

    __tag_format_flags = 41

    local_members = (
        Member(0, "value", hkInt16, MemberFlags.Private),
    )
    members = local_members

    value: int


class hkpEntityExtendedListeners(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkpEntity::ExtendedListeners"

    local_members = (
        Member(0, "activationListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
        Member(16, "entityListeners", hkpEntitySmallArraySerializeOverrideType, MemberFlags.NotSerializable),
    )
    members = local_members

    activationListeners: hkpEntitySmallArraySerializeOverrideType
    entityListeners: hkpEntitySmallArraySerializeOverrideType


class hkpMaterialResponseType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpMaterial::ResponseType"
    local_members = ()


class hkpCollidableBoundingVolumeData(hk):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpCollidable::BoundingVolumeData"

    local_members = (
        Member(0, "min", hkGenericStruct(hkUint32, 3)),
        Member(12, "expansionMin", hkGenericStruct(hkUint8, 3)),
        Member(15, "expansionShift", hkUint8),
        Member(16, "max", hkGenericStruct(hkUint32, 3)),
        Member(28, "expansionMax", hkGenericStruct(hkUint8, 3)),
        Member(31, "padding", hkUint8, MemberFlags.NotSerializable),
        Member(32, "numChildShapeAabbs", hkUint16, MemberFlags.NotSerializable),
        Member(34, "capacityChildShapeAabbs", hkUint16, MemberFlags.NotSerializable),
        Member(40, "childShapeAabbs", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(48, "childShapeKeys", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
    )
    members = local_members

    min: tuple[hkUint32]
    expansionMin: tuple[hkUint8]
    expansionShift: int
    max: tuple[hkUint32]
    expansionMax: tuple[hkUint8]
    padding: int
    numChildShapeAabbs: int
    capacityChildShapeAabbs: int
    childShapeAabbs: hkReflectDetailOpaque
    childShapeKeys: hkReflectDetailOpaque


class hkSimplePropertyValue(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "data", hkUint64),
    )
    members = local_members

    data: int


class hkpConstraintAtomAtomType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpConstraintAtom::AtomType"
    local_members = ()


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


class hkpMotionMotionType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpMotion::MotionType"
    local_members = ()


class hkUFloat8(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "value", hkUint8),
    )
    members = local_members

    value: int


class hkcdShapeTypeShapeTypeEnum(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkcdShapeType::ShapeTypeEnum"
    local_members = ()


class hkcdShapeDispatchTypeShapeDispatchTypeEnum(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkcdShapeDispatchType::ShapeDispatchTypeEnum"
    local_members = ()


class hkcdShapeInfoCodecTypeShapeInfoCodecTypeEnum(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkcdShapeInfoCodecType::ShapeInfoCodecTypeEnum"
    local_members = ()


class hkaSkeletonMapperDataPartitionMappingRange(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkaSkeletonMapperData::PartitionMappingRange"

    local_members = (
        Member(0, "startMappingIndex", _int),
        Member(4, "numMappings", _int),
    )
    members = local_members

    startMappingIndex: int
    numMappings: int


class hkaSkeletonMapperDataSimpleMapping(hk):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 483849271
    __version = 1
    __real_name = "hkaSkeletonMapperData::SimpleMapping"

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

    __tag_format_flags = 45
    __hsh = 1095861039
    __version = 1
    __real_name = "hkaSkeletonMapperData::ChainMapping"

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


class hkaSkeletonMapperDataMappingType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkaSkeletonMapperData::MappingType"
    local_members = ()


class hkpConeLimitConstraintAtomMeasurementMode(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpConeLimitConstraintAtom::MeasurementMode"
    local_members = ()


class hkpConstraintAtomSolvingMethod(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpConstraintAtom::SolvingMethod"
    local_members = ()


class hkpConstraintMotorMotorType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "hkpConstraintMotor::MotorType"
    local_members = ()


class hkRootLevelContainerNamedVariant(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3786125824
    __version = 1
    __real_name = "hkRootLevelContainer::NamedVariant"

    local_members = (
        Member(0, "name", hkStringPtr, MemberFlags.Private),
        Member(8, "className", hkStringPtr, MemberFlags.Private),
        Member(16, "variant", hkRefVariant(hkReferencedObject, hsh=2872857893), MemberFlags.Private),
    )
    members = local_members

    name: str
    className: str
    variant: hkReferencedObject


class hkaBone(hk):
    alignment = 8
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
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkaSkeleton::LocalFrameOnBone"

    local_members = (
        Member(0, "localFrame", hkRefPtr(hkLocalFrame)),
        Member(8, "boneIndex", hkInt16),
    )
    members = local_members

    localFrame: hkLocalFrame
    boneIndex: int


class hkaAnimatedReferenceFrame(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(
            16,
            "frameType",
            hkEnum(hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum, hkInt8),
            MemberFlags.NotSerializable,
        ),
    )
    members = hkReferencedObject.members + local_members

    frameType: hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum


class hkaAnnotationTrack(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 826888163

    local_members = (
        Member(0, "trackName", hkStringPtr),
        Member(8, "annotations", hkArray(hkaAnnotationTrackAnnotation)),
    )
    members = local_members

    trackName: str
    annotations: list[hkaAnnotationTrackAnnotation]


class hkxIndexBuffer(hkReferencedObject):
    alignment = 8
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(16, "indexType", hkEnum(hkxIndexBufferIndexType, hkInt8)),
        Member(24, "indices16", hkArray(hkUint16)),
        Member(40, "indices32", hkArray(hkUint32, hsh=4255738572)),
        Member(56, "vertexBaseOffset", hkUint32),
        Member(60, "length", hkUint32),
    )
    members = hkReferencedObject.members + local_members

    indexType: hkxIndexBufferIndexType
    indices16: list[int]
    indices32: list[int]
    vertexBaseOffset: int
    length: int


class hkxAttributeGroup(hk):
    alignment = 8
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
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkxMaterial::TextureStage"

    local_members = (
        Member(0, "texture", hkRefVariant(hkReferencedObject, hsh=2872857893)),
        Member(8, "usageHint", hkEnum(hkxMaterialTextureType, hkInt32)),
        Member(12, "tcoordChannel", hkInt32),
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: hkxMaterialTextureType
    tcoordChannel: int


class hkxVertexDescriptionElementDecl(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 4
    __real_name = "hkxVertexDescription::ElementDecl"

    local_members = (
        Member(0, "byteOffset", hkUint32),
        Member(4, "type", hkEnum(hkxVertexDescriptionDataType, hkUint16)),
        Member(6, "usage", hkEnum(hkxVertexDescriptionDataUsage, hkUint16)),
        Member(8, "byteStride", hkUint32),
        Member(12, "numElements", hkUint8),
        Member(16, "channelID", hkStringPtr),
    )
    members = local_members

    byteOffset: int
    type: hkxVertexDescriptionDataType
    usage: hkxVertexDescriptionDataUsage
    byteStride: int
    numElements: int
    channelID: str


class hkxVertexAnimationUsageMap(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkxVertexAnimation::UsageMap"

    local_members = (
        Member(0, "use", hkEnum(hkxVertexDescriptionDataUsage, hkUint16)),
        Member(2, "useIndexOrig", hkUint8),
        Member(3, "useIndexLocal", hkUint8),
    )
    members = local_members

    use: hkxVertexDescriptionDataUsage
    useIndexOrig: int
    useIndexLocal: int


class hkpCollisionFilter(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 121
    __abstract_value = 3

    local_members = (
        Member(48, "prepad", hkGenericStruct(hkUint32, 2)),
        Member(56, "type", hkEnum(hkpCollisionFilterhkpFilterType, hkUint32)),
        Member(60, "postpad", hkGenericStruct(hkUint32, 3)),
    )
    members = hkReferencedObject.members + local_members

    prepad: tuple[hkUint32]
    type: hkpCollisionFilterhkpFilterType
    postpad: tuple[hkUint32]

    __interfaces = (
        Interface(hkpCollidableCollidableFilter, flags=16),
        Interface(hkpShapeCollectionFilter, flags=24),
        Interface(hkpRayShapeCollectionFilter, flags=32),
        Interface(hkpRayCollidableFilter, flags=40),
    )


class hkpMaterial(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(0, "responseType", hkEnum(hkpMaterialResponseType, hkInt8), MemberFlags.Private),
        Member(2, "rollingFrictionMultiplier", hkHalf16, MemberFlags.Private),
        Member(4, "friction", hkReal, MemberFlags.Private),
        Member(8, "restitution", hkReal, MemberFlags.Private),
    )
    members = local_members

    responseType: hkpMaterialResponseType
    rollingFrictionMultiplier: float
    friction: float
    restitution: float


class hkpConstraintAtom(hk):
    alignment = 61456
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "type", hkEnum(hkpConstraintAtomAtomType, hkUint16)),
    )
    members = local_members

    type: hkpConstraintAtomAtomType


class hkSimpleProperty(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(0, "key", hkUint32),
        Member(4, "alignmentPadding", hkUint32, MemberFlags.NotSerializable),
        Member(8, "value", hkSimplePropertyValue),
    )
    members = local_members

    key: int
    alignmentPadding: int
    value: hkSimplePropertyValue


class hkpTypedBroadPhaseHandle(hkpBroadPhaseHandle):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(4, "type", hkInt8, MemberFlags.Protected),
        Member(5, "ownerOffset", hkInt8, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(6, "objectQualityType", hkInt8),
        Member(8, "collisionFilterInfo", hkUint32),
    )
    members = hkpBroadPhaseHandle.members + local_members

    type: int
    ownerOffset: int
    objectQualityType: int
    collisionFilterInfo: int


class hkMotionState(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(0, "transform", hkTransform, MemberFlags.Protected),
        Member(64, "sweptTransform", hkGenericStruct(hkVector4f, 5), MemberFlags.Protected),
        Member(144, "deltaAngle", hkVector4),
        Member(160, "objectRadius", hkReal),
        Member(164, "linearDamping", hkHalf16),
        Member(166, "angularDamping", hkHalf16),
        Member(168, "timeFactor", hkHalf16),
        Member(170, "maxLinearVelocity", hkUFloat8),
        Member(171, "maxAngularVelocity", hkUFloat8),
        Member(172, "deactivationClass", hkUint8),
    )
    members = local_members

    transform: hkTransform
    sweptTransform: tuple[hkVector4f]
    deltaAngle: hkVector4
    objectRadius: float
    linearDamping: float
    angularDamping: float
    timeFactor: float
    maxLinearVelocity: hkUFloat8
    maxAngularVelocity: hkUFloat8
    deactivationClass: int


class hkcdShape(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "type", hkEnum(hkcdShapeTypeShapeTypeEnum, hkUint8), MemberFlags.NotSerializable),
        Member(17, "dispatchType", hkEnum(hkcdShapeDispatchTypeShapeDispatchTypeEnum, hkUint8)),
        Member(18, "bitsPerKey", hkUint8),
        Member(19, "shapeInfoCodecType", hkEnum(hkcdShapeInfoCodecTypeShapeInfoCodecTypeEnum, hkUint8)),
    )
    members = hkReferencedObject.members + local_members

    type: hkcdShapeTypeShapeTypeEnum
    dispatchType: hkcdShapeDispatchTypeShapeDispatchTypeEnum
    bitsPerKey: int
    shapeInfoCodecType: hkcdShapeInfoCodecTypeShapeInfoCodecTypeEnum


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

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(2, "enabled", hkBool),
        Member(4, "maxLinImpulse", hkReal),
        Member(8, "maxAngImpulse", hkReal),
        Member(12, "maxAngle", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    enabled: bool
    maxLinImpulse: float
    maxAngImpulse: float
    maxAngle: float


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
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    firstFrictionAxis: int
    numFrictionAxes: int
    maxFrictionTorque: float


class hkpTwistLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "twistAxis", hkUint8),
        Member(4, "refAxis", hkUint8),
        Member(8, "minAngle", hkReal),
        Member(12, "maxAngle", hkReal),
        Member(16, "angularLimitsTauFactor", hkReal),
        Member(20, "angularLimitsDampFactor", hkReal),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: int
    twistAxis: int
    refAxis: int
    minAngle: float
    maxAngle: float
    angularLimitsTauFactor: float
    angularLimitsDampFactor: float


class hkpConeLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(2, "isEnabled", hkUint8),
        Member(3, "twistAxisInA", hkUint8),
        Member(4, "refAxisInB", hkUint8),
        Member(5, "angleMeasurementMode", hkEnum(hkpConeLimitConstraintAtomMeasurementMode, hkUint8)),
        Member(6, "memOffsetToAngleOffset", hkUint16),
        Member(8, "minAngle", hkReal),
        Member(12, "maxAngle", hkReal),
        Member(16, "angularLimitsTauFactor", hkReal),
        Member(20, "angularLimitsDampFactor", hkReal),
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
    angularLimitsDampFactor: float


class hkpBallSocketConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member(2, "solvingMethod", hkEnum(hkpConstraintAtomSolvingMethod, hkUint8)),
        Member(3, "bodiesToNotify", hkUint8),
        Member(4, "velocityStabilizationFactor", hkUFloat8, MemberFlags.Protected),
        Member(5, "enableLinearImpulseLimit", hkBool),
        Member(8, "breachImpulse", hkReal),
        Member(12, "inertiaStabilizationFactor", hkReal, MemberFlags.Protected),
    )
    members = hkpConstraintAtom.members + local_members

    solvingMethod: hkpConstraintAtomSolvingMethod
    bodiesToNotify: int
    velocityStabilizationFactor: hkUFloat8
    enableLinearImpulseLimit: bool
    breachImpulse: float
    inertiaStabilizationFactor: float


class hkpConstraintMotor(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(16, "type", hkEnum(hkpConstraintMotorMotorType, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    type: hkpConstraintMotorMotorType


class hkpLimitedForceConstraintMotor(hkpConstraintMotor):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(24, "minForce", hkReal),
        Member(28, "maxForce", hkReal),
    )
    members = hkpConstraintMotor.members + local_members

    minForce: float
    maxForce: float


class hkaDefaultAnimatedReferenceFrame(hkaAnimatedReferenceFrame):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2816999057

    local_members = (
        Member(32, "up", hkVector4),
        Member(48, "forward", hkVector4),
        Member(64, "duration", hkReal),
        Member(72, "referenceFrameSamples", hkArray(hkVector4, hsh=2234779563)),
    )
    members = hkaAnimatedReferenceFrame.members + local_members

    up: hkVector4
    forward: hkVector4
    duration: float
    referenceFrameSamples: list[hkVector4]


class hkRootLevelContainer(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2517046881

    local_members = (
        Member(0, "namedVariants", hkArray(hkRootLevelContainerNamedVariant, hsh=188352321)),
    )
    members = local_members

    namedVariants: list[hkRootLevelContainerNamedVariant]


class hkaSkeleton(hkReferencedObject):
    alignment = 8
    byte_size = 136
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 6

    local_members = (
        Member(16, "name", hkStringPtr),
        Member(24, "parentIndices", hkArray(hkInt16, hsh=2354433887)),
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
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 3

    local_members = (
        Member(16, "type", hkEnum(hkaAnimationAnimationType, hkInt32), MemberFlags.Protected),
        Member(20, "duration", hkReal),
        Member(24, "numberOfTransformTracks", _int),
        Member(28, "numberOfFloatTracks", _int),
        Member(
            32,
            "extractedMotion",
            hkRefPtr(hkaAnimatedReferenceFrame, hsh=686995507),
            MemberFlags.Protected,
        ),
        Member(40, "annotationTracks", hkArray(hkaAnnotationTrack, hsh=409807455)),
    )
    members = hkReferencedObject.members + local_members

    type: hkaAnimationAnimationType
    duration: float
    numberOfTransformTracks: int
    numberOfFloatTracks: int
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]


class hkaAnimationBinding(hkReferencedObject):
    alignment = 8
    byte_size = 88
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1548920428
    __version = 3

    local_members = (
        Member(16, "originalSkeletonName", hkStringPtr),
        Member(24, "animation", hkRefPtr(hkaAnimation, hsh=835592334)),
        Member(32, "transformTrackToBoneIndices", hkArray(hkInt16, hsh=2354433887)),
        Member(48, "floatTrackToFloatSlotIndices", hkArray(hkInt16, hsh=2354433887)),
        Member(64, "partitionIndices", hkArray(hkInt16, hsh=2354433887)),
        Member(80, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: str
    animation: hkaAnimation
    transformTrackToBoneIndices: list[int]
    floatTrackToFloatSlotIndices: list[int]
    partitionIndices: list[int]
    blendHint: hkaAnimationBindingBlendHint


class hkxAttributeHolder(hkReferencedObject):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(16, "attributeGroups", hkArray(hkxAttributeGroup)),
    )
    members = hkReferencedObject.members + local_members

    attributeGroups: list[hkxAttributeGroup]


class hkxMaterial(hkxAttributeHolder):
    alignment = 16
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member(32, "name", hkStringPtr),
        Member(40, "stages", hkArray(hkxMaterialTextureStage)),
        Member(64, "diffuseColor", hkVector4),
        Member(80, "ambientColor", hkVector4),
        Member(96, "specularColor", hkVector4),
        Member(112, "emissiveColor", hkVector4),
        Member(128, "subMaterials", hkArray(hkRefPtr(DefType("hkxMaterial", lambda: hkxMaterial)))),
        Member(144, "extraData", hkRefVariant(hkReferencedObject, hsh=2872857893)),
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
    uvMapScale: tuple[hkReal]
    uvMapOffset: tuple[hkReal]
    uvMapRotation: float
    uvMapAlgorithm: hkxMaterialUVMappingAlgorithm
    specularMultiplier: float
    specularExponent: float
    transparency: hkxMaterialTransparency
    userData: int
    properties: list[hkxMaterialProperty]


class hkxVertexDescription(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "decls", hkArray(hkxVertexDescriptionElementDecl)),
    )
    members = local_members

    decls: list[hkxVertexDescriptionElementDecl]


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

    gravity: hkVector4
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


class hkpModifierConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(16, "modifierAtomSize", hkUint16),
        Member(18, "childSize", hkUint16),
        Member(24, "child", Ptr(hkpConstraintAtom)),
        Member(32, "pad", hkGenericStruct(hkUint32, 2), MemberFlags.NotSerializable),
    )
    members = hkpConstraintAtom.members + local_members

    modifierAtomSize: int
    childSize: int
    child: hkpConstraintAtom
    pad: tuple[hkUint32]


class hkpMotion(hkReferencedObject):
    alignment = 16
    byte_size = 320
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 3

    local_members = (
        Member(16, "type", hkEnum(hkpMotionMotionType, hkUint8)),
        Member(17, "deactivationIntegrateCounter", hkUint8),
        Member(18, "deactivationNumInactiveFrames", hkGenericStruct(hkUint16, 2)),
        Member(32, "motionState", hkMotionState),
        Member(208, "inertiaAndMassInv", hkVector4),
        Member(224, "linearVelocity", hkVector4),
        Member(240, "angularVelocity", hkVector4),
        Member(256, "deactivationRefPosition", hkGenericStruct(hkVector4, 2)),
        Member(288, "deactivationRefOrientation", hkGenericStruct(hkUint32, 2)),
        Member(296, "savedMotion", Ptr(DefType("hkpMotion", lambda: hkpMotion))),
        Member(304, "savedQualityTypeIndex", hkUint16),
        Member(306, "gravityFactor", hkHalf16),
    )
    members = hkReferencedObject.members + local_members

    type: hkpMotionMotionType
    deactivationIntegrateCounter: int
    deactivationNumInactiveFrames: tuple[hkUint16]
    motionState: hkMotionState
    inertiaAndMassInv: hkVector4
    linearVelocity: hkVector4
    angularVelocity: hkVector4
    deactivationRefPosition: tuple[hkVector4]
    deactivationRefOrientation: tuple[hkUint32]
    savedMotion: hkpMotion
    savedQualityTypeIndex: int
    gravityFactor: float


class hkpShapeBase(hkcdShape):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkaSkeletonMapperData(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(0, "skeletonA", hkRefPtr(hkaSkeleton, hsh=1149764379)),
        Member(8, "skeletonB", hkRefPtr(hkaSkeleton, hsh=1149764379)),
        Member(16, "partitionMap", hkArray(hkInt16, hsh=2354433887)),
        Member(32, "simpleMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange)),
        Member(48, "chainMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange)),
        Member(64, "simpleMappings", hkArray(hkaSkeletonMapperDataSimpleMapping, hsh=3599982823)),
        Member(80, "chainMappings", hkArray(hkaSkeletonMapperDataChainMapping, hsh=643847644)),
        Member(96, "unmappedBones", hkArray(hkInt16, hsh=2354433887)),
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


class hkpRagdollMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(2, "isEnabled", hkBool),
        Member(4, "initializedOffset", hkInt16, MemberFlags.NotSerializable),
        Member(6, "previousTargetAnglesOffset", hkInt16, MemberFlags.NotSerializable),
        Member(16, "target_bRca", hkMatrix3),
        Member(64, "motors", hkGenericStruct(Ptr(hkpConstraintMotor, hsh=1039430764), 3)),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: bool
    initializedOffset: int
    previousTargetAnglesOffset: int
    target_bRca: hkMatrix3
    motors: tuple[hkpConstraintMotor]


class hkpPositionConstraintMotor(hkpLimitedForceConstraintMotor):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1057998472

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


class hkaSplineCompressedAnimation(hkaAnimation):
    alignment = 8
    byte_size = 176
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 469459246

    local_members = (
        Member(56, "numFrames", _int, MemberFlags.Private),
        Member(60, "numBlocks", _int, MemberFlags.Private),
        Member(64, "maxFramesPerBlock", _int, MemberFlags.Private),
        Member(68, "maskAndQuantizationSize", _int, MemberFlags.Private),
        Member(72, "blockDuration", hkReal, MemberFlags.Private),
        Member(76, "blockInverseDuration", hkReal, MemberFlags.Private),
        Member(80, "frameDuration", hkReal, MemberFlags.Private),
        Member(88, "blockOffsets", hkArray(hkUint32, hsh=4255738572), MemberFlags.Private),
        Member(104, "floatBlockOffsets", hkArray(hkUint32, hsh=4255738572), MemberFlags.Private),
        Member(120, "transformOffsets", hkArray(hkUint32, hsh=4255738572), MemberFlags.Private),
        Member(136, "floatOffsets", hkArray(hkUint32, hsh=4255738572), MemberFlags.Private),
        Member(152, "data", hkArray(hkUint8, hsh=2877151166), MemberFlags.Private),
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


class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkxMesh::UserChannelInfo"

    local_members = (
        Member(32, "name", hkStringPtr),
        Member(40, "className", hkStringPtr),
    )
    members = hkxAttributeHolder.members + local_members

    name: str
    className: str


class hkxVertexBuffer(hkReferencedObject):
    alignment = 8
    byte_size = 136
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(16, "data", hkxVertexBufferVertexData, MemberFlags.Protected),
        Member(120, "desc", hkxVertexDescription, MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    data: hkxVertexBufferVertexData
    desc: hkxVertexDescription


class hkxVertexAnimation(hkReferencedObject):
    alignment = 8
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 0

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


class hkpKeyframedRigidMotion(hkpMotion):
    alignment = 16
    byte_size = 320
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkpShape(hkpShapeBase):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(24, "userData", hkUlong),
    )
    members = hkpShapeBase.members + local_members

    userData: int


class hkaSkeletonMapper(hkReferencedObject):
    alignment = 16
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2757630080

    local_members = (
        Member(16, "mapping", hkaSkeletonMapperData),
    )
    members = hkReferencedObject.members + local_members

    mapping: hkaSkeletonMapperData


class hkpSphereRepShape(hkpShape):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkpRagdollConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 384
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpRagdollConstraintData::Atoms"

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


class hkxMeshSection(hkReferencedObject):
    alignment = 8
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member(16, "vertexBuffer", hkRefPtr(hkxVertexBuffer)),
        Member(24, "indexBuffers", hkArray(hkRefPtr(hkxIndexBuffer))),
        Member(40, "material", hkRefPtr(hkxMaterial)),
        Member(48, "userChannels", hkArray(hkRefVariant(hkReferencedObject, hsh=2872857893))),
        Member(64, "vertexAnimations", hkArray(hkRefPtr(hkxVertexAnimation))),
        Member(80, "linearKeyFrameHints", hkArray(_float)),
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


class hkpMaxSizeMotion(hkpKeyframedRigidMotion):
    alignment = 16
    byte_size = 320
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()


class hkpCdBody(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(0, "shape", Ptr(hkpShape, hsh=1200505464)),
        Member(8, "shapeKey", _unsigned_int),
        Member(16, "motion", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
        Member(24, "parent", Ptr(DefType("hkpCdBody", lambda: hkpCdBody)), MemberFlags.NotSerializable),
    )
    members = local_members

    shape: hkpShape
    shapeKey: int
    motion: hkReflectDetailOpaque
    parent: hkpCdBody


class hkpConvexShape(hkpSphereRepShape):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(32, "radius", hkReal, MemberFlags.Protected),
    )
    members = hkpSphereRepShape.members + local_members

    radius: float


class hkpRagdollConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 416
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1832134166

    local_members = (
        Member(32, "atoms", hkpRagdollConstraintDataAtoms),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpRagdollConstraintDataAtoms


class hkxMesh(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(16, "sections", hkArray(hkRefPtr(hkxMeshSection))),
        Member(32, "userChannelInfos", hkArray(hkRefPtr(hkxMeshUserChannelInfo))),
    )
    members = hkReferencedObject.members + local_members

    sections: list[hkxMeshSection]
    userChannelInfos: list[hkxMeshUserChannelInfo]


class hkpCollidable(hkpCdBody):
    alignment = 8
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(32, "ownerOffset", hkInt8, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(33, "forceCollideOntoPpu", hkUint8),
        Member(34, "shapeSizeOnSpu", hkUint16, MemberFlags.NotSerializable),
        Member(36, "broadPhaseHandle", hkpTypedBroadPhaseHandle),
        Member(48, "boundingVolumeData", hkpCollidableBoundingVolumeData, MemberFlags.NotSerializable),
        Member(104, "allowedPenetrationDepth", hkReal),
    )
    members = hkpCdBody.members + local_members

    ownerOffset: int
    forceCollideOntoPpu: int
    shapeSizeOnSpu: int
    broadPhaseHandle: hkpTypedBroadPhaseHandle
    boundingVolumeData: hkpCollidableBoundingVolumeData
    allowedPenetrationDepth: float


class hkpCapsuleShape(hkpConvexShape):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 276111070

    local_members = (
        Member(48, "vertexA", hkVector4, MemberFlags.Protected),
        Member(64, "vertexB", hkVector4, MemberFlags.Protected),
    )
    members = hkpConvexShape.members + local_members

    vertexA: hkVector4
    vertexB: hkVector4


class hkaMeshBinding(hkReferencedObject):
    alignment = 8
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(16, "mesh", hkRefPtr(hkxMesh)),
        Member(24, "originalSkeletonName", hkStringPtr),
        Member(32, "name", hkStringPtr),
        Member(40, "skeleton", hkRefPtr(hkaSkeleton)),
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


class hkpLinkedCollidable(hkpCollidable):
    alignment = 8
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(
            112,
            "collisionEntries",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
    )
    members = hkpCollidable.members + local_members

    collisionEntries: list[hkReflectDetailOpaque]


class hkaAnimationContainer(hkReferencedObject):
    alignment = 8
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3294833177
    __version = 1

    local_members = (
        Member(16, "skeletons", hkArray(hkRefPtr(hkaSkeleton))),
        Member(32, "animations", hkArray(hkRefPtr(hkaAnimation, hsh=835592334), hsh=2995419249)),
        Member(48, "bindings", hkArray(hkRefPtr(hkaAnimationBinding, hsh=2009438005), hsh=2651098392)),
        Member(64, "attachments", hkArray(hkRefPtr(hkaBoneAttachment))),
        Member(80, "skins", hkArray(hkRefPtr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]


class hkpWorldObject(hkReferencedObject):
    alignment = 8
    byte_size = 200
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(16, "world", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(24, "userData", hkUlong, MemberFlags.Protected),
        Member(32, "collidable", hkpLinkedCollidable, MemberFlags.Protected),
        Member(160, "multiThreadCheck", hkMultiThreadCheck, MemberFlags.Protected),
        Member(176, "name", hkStringPtr, MemberFlags.Protected),
        Member(184, "properties", hkArray(hkSimpleProperty)),
    )
    members = hkReferencedObject.members + local_members

    world: hkReflectDetailOpaque
    userData: int
    collidable: hkpLinkedCollidable
    multiThreadCheck: hkMultiThreadCheck
    name: str
    properties: list[hkSimpleProperty]


class hkpPhantom(hkpWorldObject):
    alignment = 8
    byte_size = 232
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(
            200,
            "overlapListeners",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            216,
            "phantomListeners",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
    )
    members = hkpWorldObject.members + local_members

    overlapListeners: list[hkReflectDetailOpaque]
    phantomListeners: list[hkReflectDetailOpaque]


class hkpEntity(hkpWorldObject):
    alignment = 16
    byte_size = 704
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member(200, "material", hkpMaterial, MemberFlags.Protected),
        Member(216, "limitContactImpulseUtilAndFlag", Ptr(_void), MemberFlags.NotSerializable),
        Member(224, "damageMultiplier", hkReal),
        Member(232, "breakableBody", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(240, "solverData", hkUint32, MemberFlags.NotSerializable),
        Member(244, "storageIndex", _unsigned_short),
        Member(246, "contactPointCallbackDelay", hkUint16, MemberFlags.Protected),
        Member(
            248,
            "constraintsMaster",
            hkpEntitySmallArraySerializeOverrideType,
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            264,
            "constraintsSlave",
            hkArray(hkViewPtr("hkpConstraintInstance", hsh=3107152142)),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(280, "constraintRuntime", hkArray(hkUint8), MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            296,
            "simulationIsland",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(304, "autoRemoveLevel", hkInt8),
        Member(305, "numShapeKeysInContactPointProperties", hkUint8),
        Member(306, "responseModifierFlags", hkUint8),
        Member(308, "uid", hkUint32),
        Member(312, "spuCollisionCallback", hkpEntitySpuCollisionCallback),
        Member(336, "motion", hkpMaxSizeMotion),
        Member(
            656,
            "contactListeners",
            hkpEntitySmallArraySerializeOverrideType,
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            672,
            "actions",
            hkpEntitySmallArraySerializeOverrideType,
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(688, "localFrame", hkRefPtr(hkLocalFrame)),
        Member(
            696,
            "extendedListeners",
            Ptr(hkpEntityExtendedListeners),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
    )
    members = hkpWorldObject.members + local_members

    material: hkpMaterial
    limitContactImpulseUtilAndFlag: _void
    damageMultiplier: float
    breakableBody: hkReflectDetailOpaque
    solverData: int
    storageIndex: int
    contactPointCallbackDelay: int
    constraintsMaster: hkpEntitySmallArraySerializeOverrideType
    constraintsSlave: list[hkpConstraintInstance]
    constraintRuntime: list[int]
    simulationIsland: hkReflectDetailOpaque
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


class hkpRigidBody(hkpEntity):
    alignment = 16
    byte_size = 704
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 74815750
    local_members = ()


class hkpConstraintInstance(hkReferencedObject):
    alignment = 8
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2242967661
    __version = 1

    local_members = (
        Member(16, "owner", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(24, "data", Ptr(hkpConstraintData, hsh=525862446), MemberFlags.Protected),
        Member(32, "constraintModifiers", Ptr(hkpModifierConstraintAtom), MemberFlags.Protected),
        Member(40, "entities", hkGenericStruct(Ptr(hkpEntity, hsh=476716456), 2), MemberFlags.Protected),
        Member(56, "priority", hkEnum(hkpConstraintInstanceConstraintPriority, hkUint8)),
        Member(57, "wantRuntime", hkBool, MemberFlags.Protected),
        Member(58, "destructionRemapInfo", hkEnum(hkpConstraintInstanceOnDestructionRemapInfo, hkUint8)),
        Member(
            64,
            "listeners",
            hkpConstraintInstanceSmallArraySerializeOverrideType,
            MemberFlags.NotSerializable,
        ),
        Member(80, "name", hkStringPtr),
        Member(88, "userData", hkUlong),
        Member(96, "internal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(104, "uid", hkUint32, MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    owner: hkReflectDetailOpaque
    data: hkpConstraintData
    constraintModifiers: hkpModifierConstraintAtom
    entities: tuple[hkpEntity]
    priority: hkpConstraintInstanceConstraintPriority
    wantRuntime: bool
    destructionRemapInfo: hkpConstraintInstanceOnDestructionRemapInfo
    listeners: hkpConstraintInstanceSmallArraySerializeOverrideType
    name: str
    userData: int
    internal: hkReflectDetailOpaque
    uid: int


class hkaRagdollInstance(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2652690323

    local_members = (
        Member(16, "rigidBodies", hkArray(Ptr(hkpRigidBody, hsh=2417329070), hsh=1736666912)),
        Member(32, "constraints", hkArray(Ptr(hkpConstraintInstance, hsh=3107152142), hsh=3091539382)),
        Member(48, "boneToRigidBodyMap", hkArray(_int, hsh=2106159949)),
        Member(64, "skeleton", hkRefPtr(hkaSkeleton, hsh=1149764379)),
    )
    members = hkReferencedObject.members + local_members

    rigidBodies: list[hkpRigidBody]
    constraints: list[hkpConstraintInstance]
    boneToRigidBodyMap: list[int]
    skeleton: hkaSkeleton


class hkpPhysicsSystem(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4219313043

    local_members = (
        Member(
            16,
            "rigidBodies",
            hkArray(Ptr(hkpRigidBody, hsh=2417329070), hsh=1736666912),
            MemberFlags.Protected,
        ),
        Member(
            32,
            "constraints",
            hkArray(Ptr(hkpConstraintInstance, hsh=3107152142), hsh=3091539382),
            MemberFlags.Protected,
        ),
        Member(48, "actions", hkArray(Ptr(hkpAction)), MemberFlags.Protected),
        Member(64, "phantoms", hkArray(Ptr(hkpPhantom)), MemberFlags.Protected),
        Member(80, "name", hkStringPtr, MemberFlags.Protected),
        Member(88, "userData", hkUlong, MemberFlags.Protected),
        Member(96, "active", hkBool, MemberFlags.Protected),
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
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3659538096

    local_members = (
        Member(16, "worldCinfo", Ptr(hkpWorldCinfo), MemberFlags.Protected),
        Member(
            24,
            "systems",
            hkArray(Ptr(hkpPhysicsSystem, hsh=339365373), hsh=4005313520),
            MemberFlags.Protected,
        ),
    )
    members = hkReferencedObject.members + local_members

    worldCinfo: hkpWorldCinfo
    systems: list[hkpPhysicsSystem]
