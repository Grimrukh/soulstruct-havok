"""Auto-generated types for Havok 2015.

Generated from files:
    c2240.hkx

"""
from __future__ import annotations
import typing as tp

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.types.core import *

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.tagfile.structs import TagFileItem
    from soulstruct_havok.packfile.structs import PackFileItemEntry


# --- Invalid Types --- #


class hkReflectDetailOpaque(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = 1

    __tag_format_flags = 9
    __real_name = "hkReflect::Detail::Opaque"
    local_members = ()


# --- Primitive Types --- #


class _int(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __hsh = 4062341138
    __real_name = "int"
    local_members = ()


class _const_char(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 3

    __tag_format_flags = 9
    __real_name = "const char*"
    local_members = ()


class _unsigned_short(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = 16388

    __tag_format_flags = 9
    __real_name = "unsigned short"
    local_members = ()


class _char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 8196

    __tag_format_flags = 9
    __hsh = 4184862313
    __real_name = "char"
    local_members = ()


class _float(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 1525253

    __tag_format_flags = 9
    __real_name = "float"
    local_members = ()


class _short(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = 16900

    __tag_format_flags = 9
    __real_name = "short"
    local_members = ()


class _signed_char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 8708

    __tag_format_flags = 9
    __real_name = "signed char"
    local_members = ()


class _unsigned_long_long(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 65540

    __tag_format_flags = 9
    __real_name = "unsigned long long"
    local_members = ()


class _unsigned_int(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 32772

    __tag_format_flags = 9
    __real_name = "unsigned int"
    local_members = ()


class _unsigned_char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 8196

    __tag_format_flags = 9
    __real_name = "unsigned char"
    local_members = ()


class _void(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = 0

    __tag_format_flags = 25
    __abstract_value = 1
    __real_name = "void"
    local_members = ()


# --- Havok Struct Types --- #


class hkVector4f(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_type_flags = 1064

    __tag_format_flags = 11
    local_members = ()


class hkQuaternionf(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_type_flags = 1064

    __tag_format_flags = 43

    local_members = (
        Member("vec", hkVector4f, offset=0, flags=32),
    )
    members = local_members

    vec: hkVector4f


class hkRotationImpl(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 48
    tag_type_flags = 3112

    __tag_format_flags = 11
    local_members = ()

    __templates = (
        TemplateType("tFT", type=_float),
    )


class hkVector4(hkVector4f):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkMatrix3Impl(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 48
    tag_type_flags = 3112

    __tag_format_flags = 11
    local_members = ()

    __templates = (
        TemplateType("tFT", type=_float),
    )


class hkMatrix4f(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    tag_type_flags = 4136

    __tag_format_flags = 43

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
    tag_type_flags = 4136

    __tag_format_flags = 43

    local_members = (
        Member("rotation", hkRotationf, offset=0, flags=34),
        Member("translation", hkVector4f, offset=48, flags=34),
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
    tag_type_flags = 7

    __tag_format_flags = 41

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
    __tag_format_flags = 0
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
    __hsh = 1556469994
    __tag_format_flags = 0
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


class hkUint32(_unsigned_int):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkUint8(_unsigned_char):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkUint64(_unsigned_long_long):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


# --- Havok Core Types --- #


class hkBaseObject(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 144
    local_members = ()


class hkReferencedObject(hkBaseObject):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("memSizeAndFlags", hkUint16, offset=8, flags=37),
        Member("refCount", hkUint16, offset=10, flags=37),
    )
    members = hkBaseObject.members + local_members

    memSizeAndFlags: hkUint16
    refCount: hkUint16


class hkContainerHeapAllocator(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 16
    local_members = ()


class hkStringPtr(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 3

    __tag_format_flags = 41
    __hsh = 2837000324

    local_members = (
        Member("stringAndFlag", _const_char, offset=0, flags=36),
    )
    members = local_members

    stringAndFlag: _const_char


class hkaBoneAttachment(hkReferencedObject):
    alignment = 16
    byte_size = 128
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member("originalSkeletonName", hkStringPtr, offset=16, flags=32),
        Member("boneFromAttachment", hkMatrix4, offset=32, flags=32),
        Member("attachment", hkRefVariant(hkReferencedObject, hsh=2872857893), offset=96, flags=32),
        Member("name", hkStringPtr, offset=104, flags=32),
        Member("boneIndex", hkInt16, offset=112, flags=32),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: hkStringPtr
    boneFromAttachment: hkMatrix4
    attachment: hkReferencedObject
    name: hkStringPtr
    boneIndex: hkInt16


class hkaSkeletonPartition(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkaSkeleton::Partition"

    local_members = (
        Member("name", hkStringPtr, offset=0, flags=32),
        Member("startBoneIndex", hkInt16, offset=8, flags=32),
        Member("numBones", hkInt16, offset=10, flags=32),
    )
    members = local_members

    name: hkStringPtr
    startBoneIndex: hkInt16
    numBones: hkInt16


class hkaAnimationAnimationType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkaAnimation::AnimationType"
    local_members = ()


class hkaAnimationBindingBlendHint(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkaAnimationBinding::BlendHint"
    local_members = ()


class hkaMeshBindingMapping(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkaMeshBinding::Mapping"

    local_members = (
        Member("mapping", hkArray(hkInt16, hsh=2354433887), offset=0, flags=32),
    )
    members = local_members

    mapping: list[hkInt16]


class hkBool(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 8194

    __tag_format_flags = 41

    local_members = (
        Member("bool", _char, offset=0, flags=36),
    )
    members = local_members

    bool: _char


class hkLocalFrame(hkReferencedObject):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3
    local_members = ()


class hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkaAnimatedReferenceFrame::hkaReferenceFrameTypeEnum"
    local_members = ()


class hkaAnnotationTrackAnnotation(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkaAnnotationTrack::Annotation"

    local_members = (
        Member("time", hkReal, offset=0, flags=32),
        Member("text", hkStringPtr, offset=8, flags=32),
    )
    members = local_members

    time: hkReal
    text: hkStringPtr


class hkMeshBoneIndexMapping(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("mapping", hkArray(hkInt16, hsh=2354433887), offset=0, flags=32),
    )
    members = local_members

    mapping: list[hkInt16]


class hkxVertexBufferVertexData(hk):
    alignment = 8
    byte_size = 104
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2
    __real_name = "hkxVertexBuffer::VertexData"

    local_members = (
        Member("vectorData", hkArray(_unsigned_int, hsh=None), offset=0, flags=32),
        Member("floatData", hkArray(_unsigned_int, hsh=None), offset=16, flags=32),
        Member("uint32Data", hkArray(hkUint32, hsh=None), offset=32, flags=32),
        Member("uint16Data", hkArray(hkUint16, hsh=None), offset=48, flags=32),
        Member("uint8Data", hkArray(hkUint8, hsh=None), offset=64, flags=32),
        Member("numVerts", hkUint32, offset=80, flags=32),
        Member("vectorStride", hkUint32, offset=84, flags=32),
        Member("floatStride", hkUint32, offset=88, flags=32),
        Member("uint32Stride", hkUint32, offset=92, flags=32),
        Member("uint16Stride", hkUint32, offset=96, flags=32),
        Member("uint8Stride", hkUint32, offset=100, flags=32),
    )
    members = local_members

    vectorData: list[_unsigned_int]
    floatData: list[_unsigned_int]
    uint32Data: list[hkUint32]
    uint16Data: list[hkUint16]
    uint8Data: list[hkUint8]
    numVerts: hkUint32
    vectorStride: hkUint32
    floatStride: hkUint32
    uint32Stride: hkUint32
    uint16Stride: hkUint32
    uint8Stride: hkUint32


class hkxMaterialUVMappingAlgorithm(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkxMaterial::UVMappingAlgorithm"
    local_members = ()


class hkxMaterialTransparency(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkxMaterial::Transparency"
    local_members = ()


class hkxMaterialProperty(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkxMaterial::Property"

    local_members = (
        Member("key", hkUint32, offset=0, flags=32),
        Member("value", hkUint32, offset=4, flags=32),
    )
    members = local_members

    key: hkUint32
    value: hkUint32


class hkxIndexBufferIndexType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkxIndexBuffer::IndexType"
    local_members = ()


class hkxAttribute(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("name", hkStringPtr, offset=0, flags=32),
        Member("value", hkRefVariant(hkReferencedObject, hsh=2872857893), offset=8, flags=32),
    )
    members = local_members

    name: hkStringPtr
    value: hkReferencedObject


class hkxMaterialTextureType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkxMaterial::TextureType"
    local_members = ()


class hkxVertexDescriptionDataType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkxVertexDescription::DataType"
    local_members = ()


class hkxVertexDescriptionDataUsage(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkxVertexDescription::DataUsage"
    local_members = ()


class hkAabb(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("min", hkVector4, offset=0, flags=32),
        Member("max", hkVector4, offset=16, flags=32),
    )
    members = local_members

    min: hkVector4
    max: hkVector4


class hkpWorldCinfoBroadPhaseType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpWorldCinfo::BroadPhaseType"
    local_members = ()


class hkpWorldCinfoBroadPhaseBorderBehaviour(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpWorldCinfo::BroadPhaseBorderBehaviour"
    local_members = ()


class hkpConvexListFilter(hkReferencedObject):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3
    local_members = ()


class hkWorldMemoryAvailableWatchDog(hkReferencedObject):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1
    local_members = ()


class hkpWorldCinfoContactPointGeneration(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpWorldCinfo::ContactPointGeneration"
    local_members = ()


class hkpWorldCinfoSimulationType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpWorldCinfo::SimulationType"
    local_members = ()


class hkpCollidableCollidableFilter(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 147
    local_members = ()


class hkpShapeCollectionFilter(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 147
    local_members = ()


class hkpRayShapeCollectionFilter(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 147
    local_members = ()


class hkpRayCollidableFilter(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 147
    local_members = ()


class hkpCollisionFilterhkpFilterType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpCollisionFilter::hkpFilterType"
    local_members = ()


class hkpAction(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("world", Ptr(hkReflectDetailOpaque, hsh=None), offset=16, flags=37),
        Member("island", Ptr(hkReflectDetailOpaque, hsh=None), offset=24, flags=37),
        Member("userData", hkUlong, offset=32, flags=34),
        Member("name", hkStringPtr, offset=40, flags=34),
    )
    members = hkReferencedObject.members + local_members

    world: hkReflectDetailOpaque
    island: hkReflectDetailOpaque
    userData: hkUlong
    name: hkStringPtr


class hkpConstraintInstanceSmallArraySerializeOverrideType(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpConstraintInstance::SmallArraySerializeOverrideType"

    local_members = (
        Member("data", Ptr(_void, hsh=None), offset=0, flags=33),
        Member("size", hkUint16, offset=8, flags=32),
        Member("capacityAndFlags", hkUint16, offset=10, flags=32),
    )
    members = local_members

    data: _void
    size: hkUint16
    capacityAndFlags: hkUint16


class hkpEntitySmallArraySerializeOverrideType(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpEntity::SmallArraySerializeOverrideType"

    local_members = (
        Member("data", Ptr(_void, hsh=None), offset=0, flags=33),
        Member("size", hkUint16, offset=8, flags=32),
        Member("capacityAndFlags", hkUint16, offset=10, flags=32),
    )
    members = local_members

    data: _void
    size: hkUint16
    capacityAndFlags: hkUint16


class hkpEntitySpuCollisionCallback(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkpEntity::SpuCollisionCallback"

    local_members = (
        Member("util", Ptr(hkReflectDetailOpaque, hsh=None), offset=0, flags=33),
        Member("capacity", hkUint16, offset=8, flags=33),
        Member("eventFilter", hkUint8, offset=10, flags=32),
        Member("userFilter", hkUint8, offset=11, flags=32),
    )
    members = local_members

    util: hkReflectDetailOpaque
    capacity: hkUint16
    eventFilter: hkUint8
    userFilter: hkUint8


class hkpConstraintData(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("userData", hkUlong, offset=16, flags=32),
    )
    members = hkReferencedObject.members + local_members

    userData: hkUlong


class hkpConstraintInstanceConstraintPriority(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpConstraintInstance::ConstraintPriority"
    local_members = ()


class hkpConstraintInstanceOnDestructionRemapInfo(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpConstraintInstance::OnDestructionRemapInfo"
    local_members = ()


class hkMultiThreadCheck(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("threadId", hkUint32, offset=0, flags=33),
        Member("stackTraceId", _int, offset=4, flags=33),
        Member("markCount", hkUint16, offset=8, flags=33),
        Member("markBitStack", hkUint16, offset=10, flags=35),
    )
    members = local_members

    threadId: hkUint32
    stackTraceId: _int
    markCount: hkUint16
    markBitStack: hkUint16


class hkHalf16(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = 476677

    __tag_format_flags = 41

    local_members = (
        Member("value", hkInt16, offset=0, flags=36),
    )
    members = local_members

    value: hkInt16


class hkpEntityExtendedListeners(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkpEntity::ExtendedListeners"

    local_members = (
        Member("activationListeners", hkpEntitySmallArraySerializeOverrideType, offset=0, flags=33),
        Member("entityListeners", hkpEntitySmallArraySerializeOverrideType, offset=16, flags=33),
    )
    members = local_members

    activationListeners: hkpEntitySmallArraySerializeOverrideType
    entityListeners: hkpEntitySmallArraySerializeOverrideType


class hkpMaterialResponseType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpMaterial::ResponseType"
    local_members = ()


class hkpCollidableBoundingVolumeData(hk):
    alignment = 8
    byte_size = 56
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpCollidable::BoundingVolumeData"

    local_members = (
        Member("min", hkStruct(hkUint32, 3, TagDataType.IsVariable2), offset=0, flags=32),
        Member("expansionMin", hkStruct(hkUint8, 3, TagDataType.IsVariable2), offset=12, flags=32),
        Member("expansionShift", hkUint8, offset=15, flags=32),
        Member("max", hkStruct(hkUint32, 3, TagDataType.IsVariable2), offset=16, flags=32),
        Member("expansionMax", hkStruct(hkUint8, 3, TagDataType.IsVariable2), offset=28, flags=32),
        Member("padding", hkUint8, offset=31, flags=33),
        Member("numChildShapeAabbs", hkUint16, offset=32, flags=33),
        Member("capacityChildShapeAabbs", hkUint16, offset=34, flags=33),
        Member("childShapeAabbs", Ptr(hkReflectDetailOpaque, hsh=None), offset=40, flags=33),
        Member("childShapeKeys", Ptr(hkReflectDetailOpaque, hsh=None), offset=48, flags=33),
    )
    members = local_members

    min: tuple[hkUint32, ...]
    expansionMin: tuple[hkUint8, ...]
    expansionShift: hkUint8
    max: tuple[hkUint32, ...]
    expansionMax: tuple[hkUint8, ...]
    padding: hkUint8
    numChildShapeAabbs: hkUint16
    capacityChildShapeAabbs: hkUint16
    childShapeAabbs: hkReflectDetailOpaque
    childShapeKeys: hkReflectDetailOpaque


class hkSimplePropertyValue(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("data", hkUint64, offset=0, flags=32),
    )
    members = local_members

    data: hkUint64


class hkpConstraintAtomAtomType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpConstraintAtom::AtomType"
    local_members = ()


class hkpBroadPhaseHandle(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("id", hkUint32, offset=0, flags=33),
    )
    members = local_members

    id: hkUint32


class hkpMotionMotionType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpMotion::MotionType"
    local_members = ()


class hkUFloat8(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("value", hkUint8, offset=0, flags=32),
    )
    members = local_members

    value: hkUint8


class hkcdShapeTypeShapeTypeEnum(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkcdShapeType::ShapeTypeEnum"
    local_members = ()


class hkcdShapeDispatchTypeShapeDispatchTypeEnum(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkcdShapeDispatchType::ShapeDispatchTypeEnum"
    local_members = ()


class hkcdShapeInfoCodecTypeShapeInfoCodecTypeEnum(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkcdShapeInfoCodecType::ShapeInfoCodecTypeEnum"
    local_members = ()


class hkaSkeletonMapperDataPartitionMappingRange(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkaSkeletonMapperData::PartitionMappingRange"

    local_members = (
        Member("startMappingIndex", _int, offset=0, flags=32),
        Member("numMappings", _int, offset=4, flags=32),
    )
    members = local_members

    startMappingIndex: _int
    numMappings: _int


class hkaSkeletonMapperDataSimpleMapping(hk):
    alignment = 16
    byte_size = 64
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 483849271
    __version = 1
    __real_name = "hkaSkeletonMapperData::SimpleMapping"

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
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1095861039
    __version = 1
    __real_name = "hkaSkeletonMapperData::ChainMapping"

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


class hkaSkeletonMapperDataMappingType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkaSkeletonMapperData::MappingType"
    local_members = ()


class hkpConeLimitConstraintAtomMeasurementMode(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpConeLimitConstraintAtom::MeasurementMode"
    local_members = ()


class hkpConstraintAtomSolvingMethod(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpConstraintAtom::SolvingMethod"
    local_members = ()


class hkpConstraintMotorMotorType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpConstraintMotor::MotorType"
    local_members = ()


class hkRootLevelContainerNamedVariant(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3786125824
    __version = 1
    __real_name = "hkRootLevelContainer::NamedVariant"

    local_members = (
        Member("name", hkStringPtr, offset=0, flags=36),
        Member("className", hkStringPtr, offset=8, flags=36),
        Member("variant", hkRefVariant(hkReferencedObject, hsh=2872857893), offset=16, flags=36),
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


class hkaBone(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3855471743

    local_members = (
        Member("name", hkStringPtr, offset=0, flags=32),
        Member("lockTranslation", hkBool, offset=8, flags=32),
    )
    members = local_members

    name: hkStringPtr
    lockTranslation: hkBool


class hkaSkeletonLocalFrameOnBone(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkaSkeleton::LocalFrameOnBone"

    local_members = (
        Member("localFrame", hkRefPtr(hkLocalFrame, hsh=None), offset=0, flags=32),
        Member("boneIndex", hkInt16, offset=8, flags=32),
    )
    members = local_members

    localFrame: hkLocalFrame
    boneIndex: hkInt16


class hkaAnimatedReferenceFrame(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("frameType", hkEnum(hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum, hkInt8), offset=16, flags=33),
    )
    members = hkReferencedObject.members + local_members

    frameType: hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum


class hkaAnnotationTrack(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("trackName", hkStringPtr, offset=0, flags=32),
        Member("annotations", hkArray(hkaAnnotationTrackAnnotation, hsh=None), offset=8, flags=32),
    )
    members = local_members

    trackName: hkStringPtr
    annotations: list[hkaAnnotationTrackAnnotation]


class hkxIndexBuffer(hkReferencedObject):
    alignment = 8
    byte_size = 64
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("indexType", hkEnum(hkxIndexBufferIndexType, hkInt8), offset=16, flags=32),
        Member("indices16", hkArray(hkUint16, hsh=None), offset=24, flags=32),
        Member("indices32", hkArray(hkUint32, hsh=None), offset=40, flags=32),
        Member("vertexBaseOffset", hkUint32, offset=56, flags=32),
        Member("length", hkUint32, offset=60, flags=32),
    )
    members = hkReferencedObject.members + local_members

    indexType: hkxIndexBufferIndexType
    indices16: list[hkUint16]
    indices32: list[hkUint32]
    vertexBaseOffset: hkUint32
    length: hkUint32


class hkxAttributeGroup(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("name", hkStringPtr, offset=0, flags=32),
        Member("attributes", hkArray(hkxAttribute, hsh=None), offset=8, flags=32),
    )
    members = local_members

    name: hkStringPtr
    attributes: list[hkxAttribute]


class hkxMaterialTextureStage(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkxMaterial::TextureStage"

    local_members = (
        Member("texture", hkRefVariant(hkReferencedObject, hsh=2872857893), offset=0, flags=32),
        Member("usageHint", hkEnum(hkxMaterialTextureType, hkInt32), offset=8, flags=32),
        Member("tcoordChannel", hkInt32, offset=12, flags=32),
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: hkxMaterialTextureType
    tcoordChannel: hkInt32


class hkxVertexDescriptionElementDecl(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 4
    __real_name = "hkxVertexDescription::ElementDecl"

    local_members = (
        Member("byteOffset", hkUint32, offset=0, flags=32),
        Member("type", hkEnum(hkxVertexDescriptionDataType, hkUint16), offset=4, flags=32),
        Member("usage", hkEnum(hkxVertexDescriptionDataUsage, hkUint16), offset=6, flags=32),
        Member("byteStride", hkUint32, offset=8, flags=32),
        Member("numElements", hkUint8, offset=12, flags=32),
        Member("channelID", hkStringPtr, offset=16, flags=32),
    )
    members = local_members

    byteOffset: hkUint32
    type: hkxVertexDescriptionDataType
    usage: hkxVertexDescriptionDataUsage
    byteStride: hkUint32
    numElements: hkUint8
    channelID: hkStringPtr


class hkxVertexAnimationUsageMap(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkxVertexAnimation::UsageMap"

    local_members = (
        Member("use", hkEnum(hkxVertexDescriptionDataUsage, hkUint16), offset=0, flags=32),
        Member("useIndexOrig", hkUint8, offset=2, flags=32),
        Member("useIndexLocal", hkUint8, offset=3, flags=32),
    )
    members = local_members

    use: hkxVertexDescriptionDataUsage
    useIndexOrig: hkUint8
    useIndexLocal: hkUint8


class hkpCollisionFilter(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = 7

    __tag_format_flags = 121
    __abstract_value = 3

    local_members = (
        Member("prepad", hkStruct(hkUint32, 2, TagDataType.IsVariable1), offset=48, flags=32),
        Member("type", hkEnum(hkpCollisionFilterhkpFilterType, hkUint32), offset=56, flags=32),
        Member("postpad", hkStruct(hkUint32, 3, TagDataType.IsVariable2), offset=60, flags=32),
    )
    members = hkReferencedObject.members + local_members

    prepad: tuple[hkUint32, ...]
    type: hkpCollisionFilterhkpFilterType
    postpad: tuple[hkUint32, ...]

    __interfaces = (
        Interface(hkpCollidableCollidableFilter, flags=16),
        Interface(hkpShapeCollectionFilter, flags=24),
        Interface(hkpRayShapeCollectionFilter, flags=32),
        Interface(hkpRayCollidableFilter, flags=40),
    )


class hkpMaterial(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member("responseType", hkEnum(hkpMaterialResponseType, hkInt8), offset=0, flags=36),
        Member("rollingFrictionMultiplier", hkHalf16, offset=2, flags=36),
        Member("friction", hkReal, offset=4, flags=36),
        Member("restitution", hkReal, offset=8, flags=36),
    )
    members = local_members

    responseType: hkpMaterialResponseType
    rollingFrictionMultiplier: hkHalf16
    friction: hkReal
    restitution: hkReal


class hkpConstraintAtom(hk):
    alignment = 61456
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("type", hkEnum(hkpConstraintAtomAtomType, hkUint16), offset=0, flags=32),
    )
    members = local_members

    type: hkpConstraintAtomAtomType


class hkSimpleProperty(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member("key", hkUint32, offset=0, flags=32),
        Member("alignmentPadding", hkUint32, offset=4, flags=33),
        Member("value", hkSimplePropertyValue, offset=8, flags=32),
    )
    members = local_members

    key: hkUint32
    alignmentPadding: hkUint32
    value: hkSimplePropertyValue


class hkpTypedBroadPhaseHandle(hkpBroadPhaseHandle):
    alignment = 4
    byte_size = 12
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("type", hkInt8, offset=4, flags=34),
        Member("ownerOffset", hkInt8, offset=5, flags=35),
        Member("objectQualityType", hkInt8, offset=6, flags=32),
        Member("collisionFilterInfo", hkUint32, offset=8, flags=32),
    )
    members = hkpBroadPhaseHandle.members + local_members

    type: hkInt8
    ownerOffset: hkInt8
    objectQualityType: hkInt8
    collisionFilterInfo: hkUint32


class hkMotionState(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member("transform", hkTransform, offset=0, flags=34),
        Member("sweptTransform", hkStruct(hkVector4f, 5, TagDataType.IsVariable3), offset=64, flags=34),
        Member("deltaAngle", hkVector4, offset=144, flags=32),
        Member("objectRadius", hkReal, offset=160, flags=32),
        Member("linearDamping", hkHalf16, offset=164, flags=32),
        Member("angularDamping", hkHalf16, offset=166, flags=32),
        Member("timeFactor", hkHalf16, offset=168, flags=32),
        Member("maxLinearVelocity", hkUFloat8, offset=170, flags=32),
        Member("maxAngularVelocity", hkUFloat8, offset=171, flags=32),
        Member("deactivationClass", hkUint8, offset=172, flags=32),
    )
    members = local_members

    transform: hkTransform
    sweptTransform: tuple[hkVector4f, ...]
    deltaAngle: hkVector4
    objectRadius: hkReal
    linearDamping: hkHalf16
    angularDamping: hkHalf16
    timeFactor: hkHalf16
    maxLinearVelocity: hkUFloat8
    maxAngularVelocity: hkUFloat8
    deactivationClass: hkUint8


class hkcdShape(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("type", hkEnum(hkcdShapeTypeShapeTypeEnum, hkUint8), offset=16, flags=33),
        Member("dispatchType", hkEnum(hkcdShapeDispatchTypeShapeDispatchTypeEnum, hkUint8), offset=17, flags=32),
        Member("bitsPerKey", hkUint8, offset=18, flags=32),
        Member("shapeInfoCodecType", hkEnum(hkcdShapeInfoCodecTypeShapeInfoCodecTypeEnum, hkUint8), offset=19, flags=32),
    )
    members = hkReferencedObject.members + local_members

    type: hkcdShapeTypeShapeTypeEnum
    dispatchType: hkcdShapeDispatchTypeShapeDispatchTypeEnum
    bitsPerKey: hkUint8
    shapeInfoCodecType: hkcdShapeInfoCodecTypeShapeInfoCodecTypeEnum


class hkpSetLocalTransformsConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 144
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("transformA", hkTransform, offset=16, flags=32),
        Member("transformB", hkTransform, offset=80, flags=32),
    )
    members = hkpConstraintAtom.members + local_members

    transformA: hkTransform
    transformB: hkTransform


class hkpSetupStabilizationAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member("enabled", hkBool, offset=2, flags=32),
        Member("maxLinImpulse", hkReal, offset=4, flags=32),
        Member("maxAngImpulse", hkReal, offset=8, flags=32),
        Member("maxAngle", hkReal, offset=12, flags=32),
    )
    members = hkpConstraintAtom.members + local_members

    enabled: hkBool
    maxLinImpulse: hkReal
    maxAngImpulse: hkReal
    maxAngle: hkReal


class hkpAngFrictionConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("isEnabled", hkUint8, offset=2, flags=32),
        Member("firstFrictionAxis", hkUint8, offset=3, flags=32),
        Member("numFrictionAxes", hkUint8, offset=4, flags=32),
        Member("maxFrictionTorque", hkReal, offset=8, flags=32),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: hkUint8
    firstFrictionAxis: hkUint8
    numFrictionAxes: hkUint8
    maxFrictionTorque: hkReal


class hkpTwistLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("isEnabled", hkUint8, offset=2, flags=32),
        Member("twistAxis", hkUint8, offset=3, flags=32),
        Member("refAxis", hkUint8, offset=4, flags=32),
        Member("minAngle", hkReal, offset=8, flags=32),
        Member("maxAngle", hkReal, offset=12, flags=32),
        Member("angularLimitsTauFactor", hkReal, offset=16, flags=32),
        Member("angularLimitsDampFactor", hkReal, offset=20, flags=32),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: hkUint8
    twistAxis: hkUint8
    refAxis: hkUint8
    minAngle: hkReal
    maxAngle: hkReal
    angularLimitsTauFactor: hkReal
    angularLimitsDampFactor: hkReal


class hkpConeLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("isEnabled", hkUint8, offset=2, flags=32),
        Member("twistAxisInA", hkUint8, offset=3, flags=32),
        Member("refAxisInB", hkUint8, offset=4, flags=32),
        Member("angleMeasurementMode", hkEnum(hkpConeLimitConstraintAtomMeasurementMode, hkUint8), offset=5, flags=32),
        Member("memOffsetToAngleOffset", hkUint16, offset=6, flags=32),
        Member("minAngle", hkReal, offset=8, flags=32),
        Member("maxAngle", hkReal, offset=12, flags=32),
        Member("angularLimitsTauFactor", hkReal, offset=16, flags=32),
        Member("angularLimitsDampFactor", hkReal, offset=20, flags=32),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: hkUint8
    twistAxisInA: hkUint8
    refAxisInB: hkUint8
    angleMeasurementMode: hkpConeLimitConstraintAtomMeasurementMode
    memOffsetToAngleOffset: hkUint16
    minAngle: hkReal
    maxAngle: hkReal
    angularLimitsTauFactor: hkReal
    angularLimitsDampFactor: hkReal


class hkpBallSocketConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member("solvingMethod", hkEnum(hkpConstraintAtomSolvingMethod, hkUint8), offset=2, flags=32),
        Member("bodiesToNotify", hkUint8, offset=3, flags=32),
        Member("velocityStabilizationFactor", hkUFloat8, offset=4, flags=34),
        Member("enableLinearImpulseLimit", hkBool, offset=5, flags=32),
        Member("breachImpulse", hkReal, offset=8, flags=32),
        Member("inertiaStabilizationFactor", hkReal, offset=12, flags=34),
    )
    members = hkpConstraintAtom.members + local_members

    solvingMethod: hkpConstraintAtomSolvingMethod
    bodiesToNotify: hkUint8
    velocityStabilizationFactor: hkUFloat8
    enableLinearImpulseLimit: hkBool
    breachImpulse: hkReal
    inertiaStabilizationFactor: hkReal


class hkpConstraintMotor(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("type", hkEnum(hkpConstraintMotorMotorType, hkInt8), offset=16, flags=32),
    )
    members = hkReferencedObject.members + local_members

    type: hkpConstraintMotorMotorType


class hkpLimitedForceConstraintMotor(hkpConstraintMotor):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("minForce", hkReal, offset=24, flags=32),
        Member("maxForce", hkReal, offset=28, flags=32),
    )
    members = hkpConstraintMotor.members + local_members

    minForce: hkReal
    maxForce: hkReal


class hkRootLevelContainer(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2517046881

    local_members = (
        Member("namedVariants", hkArray(hkRootLevelContainerNamedVariant, hsh=188352321), offset=0, flags=32),
    )
    members = local_members

    namedVariants: list[hkRootLevelContainerNamedVariant]


class hkaSkeleton(hkReferencedObject):
    alignment = 8
    byte_size = 136
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 390835893
    __version = 6

    local_members = (
        Member("name", hkStringPtr, offset=16, flags=32),
        Member("parentIndices", hkArray(hkInt16, hsh=2354433887), offset=24, flags=32),
        Member("bones", hkArray(hkaBone, hsh=1864192719), offset=40, flags=32),
        Member("referencePose", hkArray(hkQsTransform, hsh=1618709037), offset=56, flags=32),
        Member("referenceFloats", hkArray(hkReal, hsh=None), offset=72, flags=32),
        Member("floatSlots", hkArray(hkStringPtr, hsh=None), offset=88, flags=32),
        Member("localFrames", hkArray(hkaSkeletonLocalFrameOnBone, hsh=None), offset=104, flags=32),
        Member("partitions", hkArray(hkaSkeletonPartition, hsh=None), offset=120, flags=32),
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


class hkaAnimation(hkReferencedObject):
    alignment = 8
    byte_size = 56
    tag_type_flags = 7

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 3

    local_members = (
        Member("type", hkEnum(hkaAnimationAnimationType, hkInt32), offset=16, flags=34),
        Member("duration", hkReal, offset=20, flags=32),
        Member("numberOfTransformTracks", _int, offset=24, flags=32),
        Member("numberOfFloatTracks", _int, offset=28, flags=32),
        Member("extractedMotion", hkRefPtr(hkaAnimatedReferenceFrame, hsh=None), offset=32, flags=34),
        Member("annotationTracks", hkArray(hkaAnnotationTrack, hsh=None), offset=40, flags=32),
    )
    members = hkReferencedObject.members + local_members

    type: hkaAnimationAnimationType
    duration: hkReal
    numberOfTransformTracks: _int
    numberOfFloatTracks: _int
    extractedMotion: hkaAnimatedReferenceFrame
    annotationTracks: list[hkaAnnotationTrack]


class hkaAnimationBinding(hkReferencedObject):
    alignment = 8
    byte_size = 88
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member("originalSkeletonName", hkStringPtr, offset=16, flags=32),
        Member("animation", hkRefPtr(hkaAnimation, hsh=None), offset=24, flags=32),
        Member("transformTrackToBoneIndices", hkArray(hkInt16, hsh=2354433887), offset=32, flags=32),
        Member("floatTrackToFloatSlotIndices", hkArray(hkInt16, hsh=2354433887), offset=48, flags=32),
        Member("partitionIndices", hkArray(hkInt16, hsh=2354433887), offset=64, flags=32),
        Member("blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8), offset=80, flags=32),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: hkStringPtr
    animation: hkaAnimation
    transformTrackToBoneIndices: list[hkInt16]
    floatTrackToFloatSlotIndices: list[hkInt16]
    partitionIndices: list[hkInt16]
    blendHint: hkaAnimationBindingBlendHint


class hkxAttributeHolder(hkReferencedObject):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member("attributeGroups", hkArray(hkxAttributeGroup, hsh=None), offset=16, flags=32),
    )
    members = hkReferencedObject.members + local_members

    attributeGroups: list[hkxAttributeGroup]


class hkxMaterial(hkxAttributeHolder):
    alignment = 16
    byte_size = 224
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member("name", hkStringPtr, offset=32, flags=32),
        Member("stages", hkArray(hkxMaterialTextureStage, hsh=None), offset=40, flags=32),
        Member("diffuseColor", hkVector4, offset=64, flags=32),
        Member("ambientColor", hkVector4, offset=80, flags=32),
        Member("specularColor", hkVector4, offset=96, flags=32),
        Member("emissiveColor", hkVector4, offset=112, flags=32),
        Member("subMaterials", hkArray(hkRefPtr(DefType("hkxMaterial", lambda: hkxMaterial), hsh=None), hsh=None), offset=128, flags=32),
        Member("extraData", hkRefVariant(hkReferencedObject, hsh=2872857893), offset=144, flags=32),
        Member("uvMapScale", hkStruct(hkReal, 2, TagDataType.IsVariable1), offset=152, flags=32),
        Member("uvMapOffset", hkStruct(hkReal, 2, TagDataType.IsVariable1), offset=160, flags=32),
        Member("uvMapRotation", hkReal, offset=168, flags=32),
        Member("uvMapAlgorithm", hkEnum(hkxMaterialUVMappingAlgorithm, hkUint32), offset=172, flags=32),
        Member("specularMultiplier", hkReal, offset=176, flags=32),
        Member("specularExponent", hkReal, offset=180, flags=32),
        Member("transparency", hkEnum(hkxMaterialTransparency, hkUint8), offset=184, flags=32),
        Member("userData", hkUlong, offset=192, flags=32),
        Member("properties", hkArray(hkxMaterialProperty, hsh=None), offset=200, flags=34),
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


class hkxVertexDescription(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("decls", hkArray(hkxVertexDescriptionElementDecl, hsh=None), offset=0, flags=32),
    )
    members = local_members

    decls: list[hkxVertexDescriptionElementDecl]


class hkpWorldCinfo(hkReferencedObject):
    alignment = 16
    byte_size = 256
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 18

    local_members = (
        Member("gravity", hkVector4, offset=16, flags=32),
        Member("broadPhaseQuerySize", hkInt32, offset=32, flags=32),
        Member("contactRestingVelocity", hkReal, offset=36, flags=32),
        Member("broadPhaseType", hkEnum(hkpWorldCinfoBroadPhaseType, hkInt8), offset=40, flags=32),
        Member("broadPhaseBorderBehaviour", hkEnum(hkpWorldCinfoBroadPhaseBorderBehaviour, hkInt8), offset=41, flags=32),
        Member("mtPostponeAndSortBroadPhaseBorderCallbacks", hkBool, offset=42, flags=32),
        Member("broadPhaseWorldAabb", hkAabb, offset=48, flags=32),
        Member("collisionTolerance", hkReal, offset=80, flags=32),
        Member("collisionFilter", hkRefPtr(hkpCollisionFilter, hsh=None), offset=88, flags=32),
        Member("convexListFilter", hkRefPtr(hkpConvexListFilter, hsh=None), offset=96, flags=32),
        Member("expectedMaxLinearVelocity", hkReal, offset=104, flags=32),
        Member("sizeOfToiEventQueue", _int, offset=108, flags=32),
        Member("expectedMinPsiDeltaTime", hkReal, offset=112, flags=32),
        Member("memoryWatchDog", hkRefPtr(hkWorldMemoryAvailableWatchDog, hsh=None), offset=120, flags=32),
        Member("broadPhaseNumMarkers", hkInt32, offset=128, flags=32),
        Member("contactPointGeneration", hkEnum(hkpWorldCinfoContactPointGeneration, hkInt8), offset=132, flags=32),
        Member("allowToSkipConfirmedCallbacks", hkBool, offset=133, flags=32),
        Member("solverTau", hkReal, offset=136, flags=32),
        Member("solverDamp", hkReal, offset=140, flags=32),
        Member("solverIterations", hkInt32, offset=144, flags=32),
        Member("solverMicrosteps", hkInt32, offset=148, flags=32),
        Member("maxConstraintViolation", hkReal, offset=152, flags=32),
        Member("forceCoherentConstraintOrderingInSolver", hkBool, offset=156, flags=32),
        Member("snapCollisionToConvexEdgeThreshold", hkReal, offset=160, flags=32),
        Member("snapCollisionToConcaveEdgeThreshold", hkReal, offset=164, flags=32),
        Member("enableToiWeldRejection", hkBool, offset=168, flags=32),
        Member("enableDeprecatedWelding", hkBool, offset=169, flags=32),
        Member("iterativeLinearCastEarlyOutDistance", hkReal, offset=172, flags=32),
        Member("iterativeLinearCastMaxIterations", hkInt32, offset=176, flags=32),
        Member("deactivationNumInactiveFramesSelectFlag0", hkUint8, offset=180, flags=32),
        Member("deactivationNumInactiveFramesSelectFlag1", hkUint8, offset=181, flags=32),
        Member("deactivationIntegrateCounter", hkUint8, offset=182, flags=32),
        Member("shouldActivateOnRigidBodyTransformChange", hkBool, offset=183, flags=32),
        Member("deactivationReferenceDistance", hkReal, offset=184, flags=32),
        Member("toiCollisionResponseRotateNormal", hkReal, offset=188, flags=32),
        Member("useCompoundSpuElf", hkBool, offset=192, flags=32),
        Member("maxSectorsPerMidphaseCollideTask", _int, offset=196, flags=32),
        Member("maxSectorsPerNarrowphaseCollideTask", _int, offset=200, flags=32),
        Member("processToisMultithreaded", hkBool, offset=204, flags=32),
        Member("maxEntriesPerToiMidphaseCollideTask", _int, offset=208, flags=32),
        Member("maxEntriesPerToiNarrowphaseCollideTask", _int, offset=212, flags=32),
        Member("maxNumToiCollisionPairsSinglethreaded", _int, offset=216, flags=32),
        Member("numToisTillAllowedPenetrationSimplifiedToi", hkReal, offset=220, flags=32),
        Member("numToisTillAllowedPenetrationToi", hkReal, offset=224, flags=32),
        Member("numToisTillAllowedPenetrationToiHigher", hkReal, offset=228, flags=32),
        Member("numToisTillAllowedPenetrationToiForced", hkReal, offset=232, flags=32),
        Member("enableDeactivation", hkBool, offset=236, flags=32),
        Member("simulationType", hkEnum(hkpWorldCinfoSimulationType, hkInt8), offset=237, flags=32),
        Member("enableSimulationIslands", hkBool, offset=238, flags=32),
        Member("minDesiredIslandSize", hkUint32, offset=240, flags=32),
        Member("processActionsInSingleThread", hkBool, offset=244, flags=32),
        Member("allowIntegrationOfIslandsWithoutConstraintsInASeparateJob", hkBool, offset=245, flags=32),
        Member("frameMarkerPsiSnap", hkReal, offset=248, flags=32),
        Member("fireCollisionCallbacks", hkBool, offset=252, flags=32),
    )
    members = hkReferencedObject.members + local_members

    gravity: hkVector4
    broadPhaseQuerySize: hkInt32
    contactRestingVelocity: hkReal
    broadPhaseType: hkpWorldCinfoBroadPhaseType
    broadPhaseBorderBehaviour: hkpWorldCinfoBroadPhaseBorderBehaviour
    mtPostponeAndSortBroadPhaseBorderCallbacks: hkBool
    broadPhaseWorldAabb: hkAabb
    collisionTolerance: hkReal
    collisionFilter: hkpCollisionFilter
    convexListFilter: hkpConvexListFilter
    expectedMaxLinearVelocity: hkReal
    sizeOfToiEventQueue: _int
    expectedMinPsiDeltaTime: hkReal
    memoryWatchDog: hkWorldMemoryAvailableWatchDog
    broadPhaseNumMarkers: hkInt32
    contactPointGeneration: hkpWorldCinfoContactPointGeneration
    allowToSkipConfirmedCallbacks: hkBool
    solverTau: hkReal
    solverDamp: hkReal
    solverIterations: hkInt32
    solverMicrosteps: hkInt32
    maxConstraintViolation: hkReal
    forceCoherentConstraintOrderingInSolver: hkBool
    snapCollisionToConvexEdgeThreshold: hkReal
    snapCollisionToConcaveEdgeThreshold: hkReal
    enableToiWeldRejection: hkBool
    enableDeprecatedWelding: hkBool
    iterativeLinearCastEarlyOutDistance: hkReal
    iterativeLinearCastMaxIterations: hkInt32
    deactivationNumInactiveFramesSelectFlag0: hkUint8
    deactivationNumInactiveFramesSelectFlag1: hkUint8
    deactivationIntegrateCounter: hkUint8
    shouldActivateOnRigidBodyTransformChange: hkBool
    deactivationReferenceDistance: hkReal
    toiCollisionResponseRotateNormal: hkReal
    useCompoundSpuElf: hkBool
    maxSectorsPerMidphaseCollideTask: _int
    maxSectorsPerNarrowphaseCollideTask: _int
    processToisMultithreaded: hkBool
    maxEntriesPerToiMidphaseCollideTask: _int
    maxEntriesPerToiNarrowphaseCollideTask: _int
    maxNumToiCollisionPairsSinglethreaded: _int
    numToisTillAllowedPenetrationSimplifiedToi: hkReal
    numToisTillAllowedPenetrationToi: hkReal
    numToisTillAllowedPenetrationToiHigher: hkReal
    numToisTillAllowedPenetrationToiForced: hkReal
    enableDeactivation: hkBool
    simulationType: hkpWorldCinfoSimulationType
    enableSimulationIslands: hkBool
    minDesiredIslandSize: hkUint32
    processActionsInSingleThread: hkBool
    allowIntegrationOfIslandsWithoutConstraintsInASeparateJob: hkBool
    frameMarkerPsiSnap: hkReal
    fireCollisionCallbacks: hkBool


class hkpModifierConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("modifierAtomSize", hkUint16, offset=16, flags=32),
        Member("childSize", hkUint16, offset=18, flags=32),
        Member("child", Ptr(hkpConstraintAtom, hsh=None), offset=24, flags=32),
        Member("pad", hkStruct(hkUint32, 2, TagDataType.IsVariable1), offset=32, flags=33),
    )
    members = hkpConstraintAtom.members + local_members

    modifierAtomSize: hkUint16
    childSize: hkUint16
    child: hkpConstraintAtom
    pad: tuple[hkUint32, ...]


class hkpMotion(hkReferencedObject):
    alignment = 16
    byte_size = 320
    tag_type_flags = 7

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 3

    local_members = (
        Member("type", hkEnum(hkpMotionMotionType, hkUint8), offset=16, flags=32),
        Member("deactivationIntegrateCounter", hkUint8, offset=17, flags=32),
        Member("deactivationNumInactiveFrames", hkStruct(hkUint16, 2, TagDataType.IsVariable1), offset=18, flags=32),
        Member("motionState", hkMotionState, offset=32, flags=32),
        Member("inertiaAndMassInv", hkVector4, offset=208, flags=32),
        Member("linearVelocity", hkVector4, offset=224, flags=32),
        Member("angularVelocity", hkVector4, offset=240, flags=32),
        Member("deactivationRefPosition", hkStruct(hkVector4, 2, TagDataType.IsVariable1), offset=256, flags=32),
        Member("deactivationRefOrientation", hkStruct(hkUint32, 2, TagDataType.IsVariable1), offset=288, flags=32),
        Member("savedMotion", Ptr(DefType("hkpMotion", lambda: hkpMotion), hsh=None), offset=296, flags=32),
        Member("savedQualityTypeIndex", hkUint16, offset=304, flags=32),
        Member("gravityFactor", hkHalf16, offset=306, flags=32),
    )
    members = hkReferencedObject.members + local_members

    type: hkpMotionMotionType
    deactivationIntegrateCounter: hkUint8
    deactivationNumInactiveFrames: tuple[hkUint16, ...]
    motionState: hkMotionState
    inertiaAndMassInv: hkVector4
    linearVelocity: hkVector4
    angularVelocity: hkVector4
    deactivationRefPosition: tuple[hkVector4, ...]
    deactivationRefOrientation: tuple[hkUint32, ...]
    savedMotion: hkpMotion
    savedQualityTypeIndex: hkUint16
    gravityFactor: hkHalf16


class hkpShapeBase(hkcdShape):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 41
    local_members = ()


class hkaSkeletonMapperData(hk):
    alignment = 16
    byte_size = 176
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member("skeletonA", hkRefPtr(hkaSkeleton, hsh=1149764379), offset=0, flags=32),
        Member("skeletonB", hkRefPtr(hkaSkeleton, hsh=1149764379), offset=8, flags=32),
        Member("partitionMap", hkArray(hkInt16, hsh=2354433887), offset=16, flags=32),
        Member("simpleMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange, hsh=None), offset=32, flags=32),
        Member("chainMappingPartitionRanges", hkArray(hkaSkeletonMapperDataPartitionMappingRange, hsh=None), offset=48, flags=32),
        Member("simpleMappings", hkArray(hkaSkeletonMapperDataSimpleMapping, hsh=3599982823), offset=64, flags=32),
        Member("chainMappings", hkArray(hkaSkeletonMapperDataChainMapping, hsh=643847644), offset=80, flags=32),
        Member("unmappedBones", hkArray(hkInt16, hsh=2354433887), offset=96, flags=32),
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


class hkpRagdollMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 96
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("isEnabled", hkBool, offset=2, flags=32),
        Member("initializedOffset", hkInt16, offset=4, flags=33),
        Member("previousTargetAnglesOffset", hkInt16, offset=6, flags=33),
        Member("target_bRca", hkMatrix3, offset=16, flags=32),
        Member("motors", hkStruct(Ptr(hkpConstraintMotor, hsh=1039430764), 3, TagDataType.IsVariable2), offset=64, flags=32),
    )
    members = hkpConstraintAtom.members + local_members

    isEnabled: hkBool
    initializedOffset: hkInt16
    previousTargetAnglesOffset: hkInt16
    target_bRca: hkMatrix3
    motors: tuple[hkpConstraintMotor, ...]


class hkpPositionConstraintMotor(hkpLimitedForceConstraintMotor):
    alignment = 8
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 1057998472

    local_members = (
        Member("tau", hkReal, offset=32, flags=32),
        Member("damping", hkReal, offset=36, flags=32),
        Member("proportionalRecoveryVelocity", hkReal, offset=40, flags=32),
        Member("constantRecoveryVelocity", hkReal, offset=44, flags=32),
    )
    members = hkpLimitedForceConstraintMotor.members + local_members

    tau: hkReal
    damping: hkReal
    proportionalRecoveryVelocity: hkReal
    constantRecoveryVelocity: hkReal


class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 8
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkxMesh::UserChannelInfo"

    local_members = (
        Member("name", hkStringPtr, offset=32, flags=32),
        Member("className", hkStringPtr, offset=40, flags=32),
    )
    members = hkxAttributeHolder.members + local_members

    name: hkStringPtr
    className: hkStringPtr


class hkxVertexBuffer(hkReferencedObject):
    alignment = 8
    byte_size = 136
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("data", hkxVertexBufferVertexData, offset=16, flags=34),
        Member("desc", hkxVertexDescription, offset=120, flags=34),
    )
    members = hkReferencedObject.members + local_members

    data: hkxVertexBufferVertexData
    desc: hkxVertexDescription


class hkxVertexAnimation(hkReferencedObject):
    alignment = 8
    byte_size = 192
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 0

    local_members = (
        Member("time", hkReal, offset=16, flags=32),
        Member("vertData", hkxVertexBuffer, offset=24, flags=32),
        Member("vertexIndexMap", hkArray(hkInt32, hsh=None), offset=160, flags=32),
        Member("componentMap", hkArray(hkxVertexAnimationUsageMap, hsh=None), offset=176, flags=32),
    )
    members = hkReferencedObject.members + local_members

    time: hkReal
    vertData: hkxVertexBuffer
    vertexIndexMap: list[hkInt32]
    componentMap: list[hkxVertexAnimationUsageMap]


class hkpKeyframedRigidMotion(hkpMotion):
    alignment = 16
    byte_size = 320
    tag_type_flags = 7

    __tag_format_flags = 41
    local_members = ()


class hkpShape(hkpShapeBase):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("userData", hkUlong, offset=24, flags=32),
    )
    members = hkpShapeBase.members + local_members

    userData: hkUlong


class hkaSkeletonMapper(hkReferencedObject):
    alignment = 16
    byte_size = 192
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2757630080

    local_members = (
        Member("mapping", hkaSkeletonMapperData, offset=16, flags=32),
    )
    members = hkReferencedObject.members + local_members

    mapping: hkaSkeletonMapperData


class hkpSphereRepShape(hkpShape):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 41
    local_members = ()


class hkpRagdollConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 384
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpRagdollConstraintData::Atoms"

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


class hkxMeshSection(hkReferencedObject):
    alignment = 8
    byte_size = 112
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member("vertexBuffer", hkRefPtr(hkxVertexBuffer, hsh=None), offset=16, flags=32),
        Member("indexBuffers", hkArray(hkRefPtr(hkxIndexBuffer, hsh=None), hsh=None), offset=24, flags=32),
        Member("material", hkRefPtr(hkxMaterial, hsh=None), offset=40, flags=32),
        Member("userChannels", hkArray(hkRefVariant(hkReferencedObject, hsh=2872857893), hsh=None), offset=48, flags=32),
        Member("vertexAnimations", hkArray(hkRefPtr(hkxVertexAnimation, hsh=None), hsh=None), offset=64, flags=32),
        Member("linearKeyFrameHints", hkArray(_float, hsh=None), offset=80, flags=32),
        Member("boneMatrixMap", hkArray(hkMeshBoneIndexMapping, hsh=None), offset=96, flags=32),
    )
    members = hkReferencedObject.members + local_members

    vertexBuffer: hkxVertexBuffer
    indexBuffers: list[hkxIndexBuffer]
    material: hkxMaterial
    userChannels: list[hkReferencedObject]
    vertexAnimations: list[hkxVertexAnimation]
    linearKeyFrameHints: list[_float]
    boneMatrixMap: list[hkMeshBoneIndexMapping]


class hkpMaxSizeMotion(hkpKeyframedRigidMotion):
    alignment = 16
    byte_size = 320
    tag_type_flags = 7

    __tag_format_flags = 41
    local_members = ()


class hkpCdBody(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member("shape", Ptr(hkpShape, hsh=1200505464), offset=0, flags=32),
        Member("shapeKey", _unsigned_int, offset=8, flags=32),
        Member("motion", Ptr(hkReflectDetailOpaque, hsh=None), offset=16, flags=37),
        Member("parent", Ptr(DefType("hkpCdBody", lambda: hkpCdBody), hsh=None), offset=24, flags=33),
    )
    members = local_members

    shape: hkpShape
    shapeKey: _unsigned_int
    motion: hkReflectDetailOpaque
    parent: hkpCdBody


class hkpConvexShape(hkpSphereRepShape):
    alignment = 8
    byte_size = 40
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("radius", hkReal, offset=32, flags=34),
    )
    members = hkpSphereRepShape.members + local_members

    radius: hkReal


class hkpRagdollConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 416
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 1832134166

    local_members = (
        Member("atoms", hkpRagdollConstraintDataAtoms, offset=32, flags=32),
    )
    members = hkpConstraintData.members + local_members

    atoms: hkpRagdollConstraintDataAtoms


class hkxMesh(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("sections", hkArray(hkRefPtr(hkxMeshSection, hsh=None), hsh=None), offset=16, flags=32),
        Member("userChannelInfos", hkArray(hkRefPtr(hkxMeshUserChannelInfo, hsh=None), hsh=None), offset=32, flags=32),
    )
    members = hkReferencedObject.members + local_members

    sections: list[hkxMeshSection]
    userChannelInfos: list[hkxMeshUserChannelInfo]


class hkpCollidable(hkpCdBody):
    alignment = 8
    byte_size = 112
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member("ownerOffset", hkInt8, offset=32, flags=35),
        Member("forceCollideOntoPpu", hkUint8, offset=33, flags=32),
        Member("shapeSizeOnSpu", hkUint16, offset=34, flags=33),
        Member("broadPhaseHandle", hkpTypedBroadPhaseHandle, offset=36, flags=32),
        Member("boundingVolumeData", hkpCollidableBoundingVolumeData, offset=48, flags=33),
        Member("allowedPenetrationDepth", hkReal, offset=104, flags=32),
    )
    members = hkpCdBody.members + local_members

    ownerOffset: hkInt8
    forceCollideOntoPpu: hkUint8
    shapeSizeOnSpu: hkUint16
    broadPhaseHandle: hkpTypedBroadPhaseHandle
    boundingVolumeData: hkpCollidableBoundingVolumeData
    allowedPenetrationDepth: hkReal


class hkpCapsuleShape(hkpConvexShape):
    alignment = 16
    byte_size = 80
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 276111070

    local_members = (
        Member("vertexA", hkVector4, offset=48, flags=34),
        Member("vertexB", hkVector4, offset=64, flags=34),
    )
    members = hkpConvexShape.members + local_members

    vertexA: hkVector4
    vertexB: hkVector4


class hkaMeshBinding(hkReferencedObject):
    alignment = 8
    byte_size = 80
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member("mesh", hkRefPtr(hkxMesh, hsh=None), offset=16, flags=32),
        Member("originalSkeletonName", hkStringPtr, offset=24, flags=32),
        Member("name", hkStringPtr, offset=32, flags=32),
        Member("skeleton", hkRefPtr(hkaSkeleton, hsh=1149764379), offset=40, flags=32),
        Member("mappings", hkArray(hkaMeshBindingMapping, hsh=None), offset=48, flags=32),
        Member("boneFromSkinMeshTransforms", hkArray(hkTransform, hsh=None), offset=64, flags=32),
    )
    members = hkReferencedObject.members + local_members

    mesh: hkxMesh
    originalSkeletonName: hkStringPtr
    name: hkStringPtr
    skeleton: hkaSkeleton
    mappings: list[hkaMeshBindingMapping]
    boneFromSkinMeshTransforms: list[hkTransform]


class hkpLinkedCollidable(hkpCollidable):
    alignment = 8
    byte_size = 128
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("collisionEntries", hkArray(hkReflectDetailOpaque, hsh=None), offset=112, flags=35),
    )
    members = hkpCollidable.members + local_members

    collisionEntries: list[hkReflectDetailOpaque]


class hkaAnimationContainer(hkReferencedObject):
    alignment = 8
    byte_size = 96
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3294833177
    __version = 1

    local_members = (
        Member("skeletons", hkArray(hkRefPtr(hkaSkeleton, hsh=1149764379), hsh=343024117), offset=16, flags=32),
        Member("animations", hkArray(hkRefPtr(hkaAnimation, hsh=None), hsh=None), offset=32, flags=32),
        Member("bindings", hkArray(hkRefPtr(hkaAnimationBinding, hsh=None), hsh=None), offset=48, flags=32),
        Member("attachments", hkArray(hkRefPtr(hkaBoneAttachment, hsh=None), hsh=None), offset=64, flags=32),
        Member("skins", hkArray(hkRefPtr(hkaMeshBinding, hsh=None), hsh=None), offset=80, flags=32),
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
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("world", Ptr(hkReflectDetailOpaque, hsh=None), offset=16, flags=35),
        Member("userData", hkUlong, offset=24, flags=34),
        Member("collidable", hkpLinkedCollidable, offset=32, flags=34),
        Member("multiThreadCheck", hkMultiThreadCheck, offset=160, flags=34),
        Member("name", hkStringPtr, offset=176, flags=34),
        Member("properties", hkArray(hkSimpleProperty, hsh=None), offset=184, flags=32),
    )
    members = hkReferencedObject.members + local_members

    world: hkReflectDetailOpaque
    userData: hkUlong
    collidable: hkpLinkedCollidable
    multiThreadCheck: hkMultiThreadCheck
    name: hkStringPtr
    properties: list[hkSimpleProperty]


class hkpPhantom(hkpWorldObject):
    alignment = 8
    byte_size = 232
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("overlapListeners", hkArray(hkReflectDetailOpaque, hsh=None), offset=200, flags=35),
        Member("phantomListeners", hkArray(hkReflectDetailOpaque, hsh=None), offset=216, flags=35),
    )
    members = hkpWorldObject.members + local_members

    overlapListeners: list[hkReflectDetailOpaque]
    phantomListeners: list[hkReflectDetailOpaque]


class hkpEntity(hkpWorldObject):
    alignment = 16
    byte_size = 704
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member("material", hkpMaterial, offset=200, flags=34),
        Member("limitContactImpulseUtilAndFlag", Ptr(_void, hsh=None), offset=216, flags=33),
        Member("damageMultiplier", hkReal, offset=224, flags=32),
        Member("breakableBody", Ptr(hkReflectDetailOpaque, hsh=None), offset=232, flags=33),
        Member("solverData", hkUint32, offset=240, flags=33),
        Member("storageIndex", _unsigned_short, offset=244, flags=32),
        Member("contactPointCallbackDelay", hkUint16, offset=246, flags=34),
        Member("constraintsMaster", hkpEntitySmallArraySerializeOverrideType, offset=248, flags=35),
        Member("constraintsSlave", hkArray(hkViewPtr("hkpConstraintInstance", hsh=3107152142), hsh=None), offset=264, flags=35),
        Member("constraintRuntime", hkArray(hkUint8, hsh=None), offset=280, flags=35),
        Member("simulationIsland", Ptr(hkReflectDetailOpaque, hsh=None), offset=296, flags=35),
        Member("autoRemoveLevel", hkInt8, offset=304, flags=32),
        Member("numShapeKeysInContactPointProperties", hkUint8, offset=305, flags=32),
        Member("responseModifierFlags", hkUint8, offset=306, flags=32),
        Member("uid", hkUint32, offset=308, flags=32),
        Member("spuCollisionCallback", hkpEntitySpuCollisionCallback, offset=312, flags=32),
        Member("motion", hkpMaxSizeMotion, offset=336, flags=32),
        Member("contactListeners", hkpEntitySmallArraySerializeOverrideType, offset=656, flags=35),
        Member("actions", hkpEntitySmallArraySerializeOverrideType, offset=672, flags=35),
        Member("localFrame", hkRefPtr(hkLocalFrame, hsh=None), offset=688, flags=32),
        Member("extendedListeners", Ptr(hkpEntityExtendedListeners, hsh=None), offset=696, flags=35),
    )
    members = hkpWorldObject.members + local_members

    material: hkpMaterial
    limitContactImpulseUtilAndFlag: _void
    damageMultiplier: hkReal
    breakableBody: hkReflectDetailOpaque
    solverData: hkUint32
    storageIndex: _unsigned_short
    contactPointCallbackDelay: hkUint16
    constraintsMaster: hkpEntitySmallArraySerializeOverrideType
    constraintsSlave: list[hkpConstraintInstance]
    constraintRuntime: list[hkUint8]
    simulationIsland: hkReflectDetailOpaque
    autoRemoveLevel: hkInt8
    numShapeKeysInContactPointProperties: hkUint8
    responseModifierFlags: hkUint8
    uid: hkUint32
    spuCollisionCallback: hkpEntitySpuCollisionCallback
    motion: hkpMaxSizeMotion
    contactListeners: hkpEntitySmallArraySerializeOverrideType
    actions: hkpEntitySmallArraySerializeOverrideType
    localFrame: hkLocalFrame
    extendedListeners: hkpEntityExtendedListeners


class hkpRigidBody(hkpEntity):
    alignment = 16
    byte_size = 704
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 74815750
    local_members = ()


class hkpConstraintInstance(hkReferencedObject):
    alignment = 8
    byte_size = 112
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 2242967661
    __version = 1

    local_members = (
        Member("owner", Ptr(hkReflectDetailOpaque, hsh=None), offset=16, flags=35),
        Member("data", Ptr(hkpConstraintData, hsh=525862446), offset=24, flags=34),
        Member("constraintModifiers", Ptr(hkpModifierConstraintAtom, hsh=None), offset=32, flags=34),
        Member("entities", hkStruct(Ptr(hkpEntity, hsh=476716456), 2, TagDataType.IsVariable1), offset=40, flags=34),
        Member("priority", hkEnum(hkpConstraintInstanceConstraintPriority, hkUint8), offset=56, flags=32),
        Member("wantRuntime", hkBool, offset=57, flags=34),
        Member("destructionRemapInfo", hkEnum(hkpConstraintInstanceOnDestructionRemapInfo, hkUint8), offset=58, flags=32),
        Member("listeners", hkpConstraintInstanceSmallArraySerializeOverrideType, offset=64, flags=33),
        Member("name", hkStringPtr, offset=80, flags=32),
        Member("userData", hkUlong, offset=88, flags=32),
        Member("internal", Ptr(hkReflectDetailOpaque, hsh=None), offset=96, flags=33),
        Member("uid", hkUint32, offset=104, flags=33),
    )
    members = hkReferencedObject.members + local_members

    owner: hkReflectDetailOpaque
    data: hkpConstraintData
    constraintModifiers: hkpModifierConstraintAtom
    entities: tuple[hkpEntity, ...]
    priority: hkpConstraintInstanceConstraintPriority
    wantRuntime: hkBool
    destructionRemapInfo: hkpConstraintInstanceOnDestructionRemapInfo
    listeners: hkpConstraintInstanceSmallArraySerializeOverrideType
    name: hkStringPtr
    userData: hkUlong
    internal: hkReflectDetailOpaque
    uid: hkUint32


class hkaRagdollInstance(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2652690323

    local_members = (
        Member("rigidBodies", hkArray(Ptr(hkpRigidBody, hsh=2417329070), hsh=1736666912), offset=16, flags=32),
        Member("constraints", hkArray(Ptr(hkpConstraintInstance, hsh=3107152142), hsh=3091539382), offset=32, flags=32),
        Member("boneToRigidBodyMap", hkArray(_int, hsh=2106159949), offset=48, flags=32),
        Member("skeleton", hkRefPtr(hkaSkeleton, hsh=1149764379), offset=64, flags=32),
    )
    members = hkReferencedObject.members + local_members

    rigidBodies: list[hkpRigidBody]
    constraints: list[hkpConstraintInstance]
    boneToRigidBodyMap: list[_int]
    skeleton: hkaSkeleton


class hkpPhysicsSystem(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 4219313043

    local_members = (
        Member("rigidBodies", hkArray(Ptr(hkpRigidBody, hsh=2417329070), hsh=1736666912), offset=16, flags=34),
        Member("constraints", hkArray(Ptr(hkpConstraintInstance, hsh=3107152142), hsh=3091539382), offset=32, flags=34),
        Member("actions", hkArray(Ptr(hkpAction, hsh=None), hsh=None), offset=48, flags=34),
        Member("phantoms", hkArray(Ptr(hkpPhantom, hsh=None), hsh=None), offset=64, flags=34),
        Member("name", hkStringPtr, offset=80, flags=34),
        Member("userData", hkUlong, offset=88, flags=34),
        Member("active", hkBool, offset=96, flags=34),
    )
    members = hkReferencedObject.members + local_members

    rigidBodies: list[hkpRigidBody]
    constraints: list[hkpConstraintInstance]
    actions: list[hkpAction]
    phantoms: list[hkpPhantom]
    name: hkStringPtr
    userData: hkUlong
    active: hkBool


class hkpPhysicsData(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3659538096

    local_members = (
        Member("worldCinfo", Ptr(hkpWorldCinfo, hsh=None), offset=16, flags=34),
        Member("systems", hkArray(Ptr(hkpPhysicsSystem, hsh=339365373), hsh=4005313520), offset=24, flags=34),
    )
    members = hkReferencedObject.members + local_members

    worldCinfo: hkpWorldCinfo
    systems: list[hkpPhysicsSystem]


class hkp2dAngConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("freeRotationAxis", hkUint8, offset=2, flags=32),
        Member("padding", hkStruct(hkUint8, 13), offset=3, flags=32),
    )

    freeRotationAxis: hkUint8
    padding: tuple[hkUint8]


class hkpAngMotorConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("isEnabled", hkBool, offset=2, flags=32),
        Member("motorAxis", hkUint8, offset=3, flags=32),
        Member("initializedOffset", hkInt16, offset=4, flags=33),
        Member("previousTargetAngleOffset", hkInt16, offset=6, flags=33),
        Member("correspondingAngLimitSolverResultOffset", hkInt16, offset=8, flags=32),
        Member("targetAngle", hkReal, offset=12, flags=32),
        Member("motor", Ptr(hkpConstraintMotor), offset=16, flags=32),
    )


class hkpAngLimitConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("isEnabled", hkUint8, offset=2, flags=32),
        Member("limitAxis", hkUint8, offset=3, flags=32),
        Member("minAngle", hkReal, offset=4, flags=32),
        Member("maxAngle", hkReal, offset=8, flags=32),
        Member("angularLimitsTauFactor", hkReal, offset=12, flags=32),
    )


class hkpLimitedHingeConstraintDataAtoms(hk):
    alignment = 16
    byte_size = 272
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member("transforms", hkpSetLocalTransformsConstraintAtom, offset=0, flags=32),
        Member("setupStabilization", hkpSetupStabilizationAtom, offset=144, flags=32),
        Member("angMotor", hkpAngMotorConstraintAtom, offset=160, flags=32),
        Member("angFriction", hkpAngFrictionConstraintAtom, offset=192, flags=32),
        Member("angLimit", hkpAngLimitConstraintAtom, offset=208, flags=32),
        Member("2dAng", hkp2dAngConstraintAtom, offset=240, flags=32),
        Member("ballSocket", hkpBallSocketConstraintAtom, offset=256, flags=32),
    )


class hkpLimitedHingeConstraintData(hkpConstraintData):
    alignment = 16
    byte_size = 304
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("atoms", hkpLimitedHingeConstraintDataAtoms, offset=32, flags=32),
    )


# FROM MAP COLLISION:


class hkQuaternion(hkQuaternionf):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkpShapeContainer(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 147
    local_members = ()


class hkpBvTreeShapeBvTreeType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpBvTreeShape::BvTreeType"
    local_members = ()


class hkpMoppCodeCodeInfo(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkpMoppCode::CodeInfo"

    local_members = (
        Member("offset", hkVector4, offset=0, flags=32),
    )
    members = local_members

    offset: hkVector4


class hkpMoppCodeBuildType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpMoppCode::BuildType"
    local_members = ()


class _CustomMeshParameter(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 4160631638
    __real_name = "CustomMeshParameter"

    local_members = (
        Member("version", hkUint32, offset=16, flags=36),
        Member("vertexDataBuffer", hkArray(hkUint8, hsh=2877151166), offset=24, flags=36),
        Member("vertexDataStride", hkInt32, offset=40, flags=36),
        Member("primitiveDataBuffer", hkArray(hkUint8, hsh=2877151166), offset=48, flags=36),
        Member("materialNameData", hkUint32, offset=64, flags=36),
    )
    members = hkReferencedObject.members + local_members

    version: hkUint32
    vertexDataBuffer: list[hkUint8]
    vertexDataStride: hkInt32
    primitiveDataBuffer: list[hkUint8]
    materialNameData: hkUint32


class hkpExtendedMeshShapeSubpart(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3
    __real_name = "hkpExtendedMeshShape::Subpart"

    local_members = (
        Member("typeAndFlags", hkUint16, offset=0, flags=34),
        Member("shapeInfo", hkUint16, offset=2, flags=32),
        Member("materialStriding", hkInt16, offset=4, flags=33),
        Member("materialIndexStriding", hkUint16, offset=6, flags=32),
        Member("materialIndexBase", Ptr(hkReflectDetailOpaque, hsh=None), offset=8, flags=33),
        Member("materialBase", Ptr(hkReflectDetailOpaque, hsh=None), offset=16, flags=33),
        Member("userData", hkUlong, offset=24, flags=32),
    )
    members = local_members

    typeAndFlags: hkUint16
    shapeInfo: hkUint16
    materialStriding: hkInt16
    materialIndexStriding: hkUint16
    materialIndexBase: hkReflectDetailOpaque
    materialBase: hkReflectDetailOpaque
    userData: hkUlong


class hkpWeldingUtilityWeldingType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpWeldingUtility::WeldingType"
    local_members = ()


class hkpShapeCollectionCollectionType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpShapeCollection::CollectionType"
    local_members = ()


class hkpExtendedMeshShapeIndexStridingType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkpExtendedMeshShape::IndexStridingType"
    local_members = ()


class hkpMeshMaterial(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("filterInfo", hkUint32, offset=0, flags=32),
    )
    members = local_members

    filterInfo: hkUint32


class hkpMoppCode(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 1660805132

    local_members = (
        Member("info", hkpMoppCodeCodeInfo, offset=16, flags=32),
        Member("data", hkArray(hkUint8, hsh=2877151166), offset=32, flags=32),
        Member("buildType", hkEnum(hkpMoppCodeBuildType, hkInt8), offset=48, flags=32),
    )
    members = hkReferencedObject.members + local_members

    info: hkpMoppCodeCodeInfo
    data: list[hkUint8]
    buildType: hkpMoppCodeBuildType


class hkpExtendedMeshShapeTrianglesSubpart(hkpExtendedMeshShapeSubpart):
    alignment = 16
    byte_size = 144
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1411582562
    __version = 4
    __real_name = "hkpExtendedMeshShape::TrianglesSubpart"

    local_members = (
        Member("numTriangleShapes", _int, offset=32, flags=32),
        Member("vertexBase", Ptr(hkReflectDetailOpaque, hsh=None), offset=40, flags=33),
        Member("numVertices", _int, offset=48, flags=32),
        Member("indexBase", Ptr(hkReflectDetailOpaque, hsh=None), offset=56, flags=33),
        Member("vertexStriding", hkUint16, offset=64, flags=32),
        Member("triangleOffset", _int, offset=68, flags=32),
        Member("indexStriding", hkUint16, offset=72, flags=32),
        Member("stridingType", hkEnum(hkpExtendedMeshShapeIndexStridingType, hkInt8), offset=74, flags=32),
        Member("flipAlternateTriangles", hkInt8, offset=75, flags=32),
        Member("extrusion", hkVector4, offset=80, flags=32),
        Member("transform", hkQsTransform, offset=96, flags=32),
    )
    members = hkpExtendedMeshShapeSubpart.members + local_members

    numTriangleShapes: _int
    vertexBase: hkReflectDetailOpaque
    numVertices: _int
    indexBase: hkReflectDetailOpaque
    vertexStriding: hkUint16
    triangleOffset: _int
    indexStriding: hkUint16
    stridingType: hkpExtendedMeshShapeIndexStridingType
    flipAlternateTriangles: hkInt8
    extrusion: hkVector4
    transform: hkQsTransform


class hkpStorageExtendedMeshShapeMaterial(hkpMeshMaterial):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpStorageExtendedMeshShape::Material"

    local_members = (
        Member("restitution", hkHalf16, offset=4, flags=32),
        Member("friction", hkHalf16, offset=6, flags=32),
        Member("userData", hkUlong, offset=8, flags=32),
    )
    members = hkpMeshMaterial.members + local_members

    restitution: hkHalf16
    friction: hkHalf16
    userData: hkUlong


class hkpNamedMeshMaterial(hkpMeshMaterial):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("name", hkStringPtr, offset=8, flags=32),
    )
    members = hkpMeshMaterial.members + local_members

    name: hkStringPtr


class hkpStorageExtendedMeshShapeMeshSubpartStorage(hkReferencedObject):
    alignment = 8
    byte_size = 144
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1824184153
    __version = 3
    __real_name = "hkpStorageExtendedMeshShape::MeshSubpartStorage"

    local_members = (
        Member("vertices", hkArray(hkVector4, hsh=2234779563), offset=16, flags=32),
        Member("indices8", hkArray(hkUint8, hsh=2877151166), offset=32, flags=32),
        Member("indices16", hkArray(hkUint16, hsh=3551656838), offset=48, flags=32),
        Member("indices32", hkArray(hkUint32, hsh=None), offset=64, flags=32),
        Member("materialIndices", hkArray(hkUint8, hsh=2877151166), offset=80, flags=32),
        Member("materials", hkArray(hkpStorageExtendedMeshShapeMaterial, hsh=None), offset=96, flags=32),
        Member("namedMaterials", hkArray(hkpNamedMeshMaterial, hsh=None), offset=112, flags=32),
        Member("materialIndices16", hkArray(hkUint16, hsh=3551656838), offset=128, flags=32),
    )
    members = hkReferencedObject.members + local_members

    vertices: list[hkVector4]
    indices8: list[hkUint8]
    indices16: list[hkUint16]
    indices32: list[hkUint32]
    materialIndices: list[hkUint8]
    materials: list[hkpStorageExtendedMeshShapeMaterial]
    namedMaterials: list[hkpNamedMeshMaterial]
    materialIndices16: list[hkUint16]


class hkpStorageExtendedMeshShapeShapeSubpartStorage(hkReferencedObject):
    alignment = 8
    byte_size = 64
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2
    __real_name = "hkpStorageExtendedMeshShape::ShapeSubpartStorage"

    local_members = (
        Member("materialIndices", hkArray(hkUint8, hsh=2877151166), offset=16, flags=32),
        Member("materials", hkArray(hkpStorageExtendedMeshShapeMaterial, hsh=None), offset=32, flags=32),
        Member("materialIndices16", hkArray(hkUint16, hsh=3551656838), offset=48, flags=32),
    )
    members = hkReferencedObject.members + local_members

    materialIndices: list[hkUint8]
    materials: list[hkpStorageExtendedMeshShapeMaterial]
    materialIndices16: list[hkUint16]


class hkpSingleShapeContainer(hkpShapeContainer):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("childShape", Ptr(hkpShape, hsh=1200505464), offset=8, flags=34),
    )
    members = hkpShapeContainer.members + local_members

    childShape: hkpShape


class hkpBvTreeShape(hkpShape):
    alignment = 8
    byte_size = 40
    tag_type_flags = 7

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1

    local_members = (
        Member("bvTreeType", hkEnum(hkpBvTreeShapeBvTreeType, hkUint8), offset=32, flags=32),
    )
    members = hkpShape.members + local_members

    bvTreeType: hkpBvTreeShapeBvTreeType


class hkpShapeCollection(hkpShape):
    alignment = 8
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 121
    __abstract_value = 3

    local_members = (
        Member("disableWelding", hkBool, offset=40, flags=32),
        Member("collectionType", hkEnum(hkpShapeCollectionCollectionType, hkUint8), offset=41, flags=32),
    )
    members = hkpShape.members + local_members

    disableWelding: hkBool
    collectionType: hkpShapeCollectionCollectionType

    __interfaces = (
        Interface(hkpShapeContainer, flags=32),
    )


class hkpSphereRepShape(hkpShape):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 41
    local_members = ()


class hkpCdBody(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member("shape", Ptr(hkpShape, hsh=1200505464), offset=0, flags=32),
        Member("shapeKey", _unsigned_int, offset=8, flags=32),
        Member("motion", Ptr(hkReflectDetailOpaque, hsh=None), offset=16, flags=37),
        Member("parent", Ptr(DefType("hkpCdBody", lambda: hkpCdBody), hsh=None), offset=24, flags=33),
    )
    members = local_members

    shape: hkpShape
    shapeKey: _unsigned_int
    motion: hkReflectDetailOpaque
    parent: hkpCdBody


class hkMoppBvTreeShapeBase(hkpBvTreeShape):
    alignment = 16
    byte_size = 80
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("code", Ptr(hkpMoppCode, hsh=3878741831), offset=40, flags=32),
        Member("moppData", Ptr(hkReflectDetailOpaque, hsh=None), offset=48, flags=33),
        Member("moppDataSize", hkUint32, offset=56, flags=33),
        Member("codeInfoCopy", hkVector4, offset=64, flags=33),
    )
    members = hkpBvTreeShape.members + local_members

    code: hkpMoppCode
    moppData: hkReflectDetailOpaque
    moppDataSize: hkUint32
    codeInfoCopy: hkVector4


class hkpConvexShape(hkpSphereRepShape):
    alignment = 8
    byte_size = 40
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("radius", hkReal, offset=32, flags=34),
    )
    members = hkpSphereRepShape.members + local_members

    radius: hkReal


class hkpCollidable(hkpCdBody):
    alignment = 8
    byte_size = 112
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member("ownerOffset", hkInt8, offset=32, flags=35),
        Member("forceCollideOntoPpu", hkUint8, offset=33, flags=32),
        Member("shapeSizeOnSpu", hkUint16, offset=34, flags=33),
        Member("broadPhaseHandle", hkpTypedBroadPhaseHandle, offset=36, flags=32),
        Member("boundingVolumeData", hkpCollidableBoundingVolumeData, offset=48, flags=33),
        Member("allowedPenetrationDepth", hkReal, offset=104, flags=32),
    )
    members = hkpCdBody.members + local_members

    ownerOffset: hkInt8
    forceCollideOntoPpu: hkUint8
    shapeSizeOnSpu: hkUint16
    broadPhaseHandle: hkpTypedBroadPhaseHandle
    boundingVolumeData: hkpCollidableBoundingVolumeData
    allowedPenetrationDepth: hkReal


class hkpMoppBvTreeShape(hkMoppBvTreeShapeBase):
    alignment = 16
    byte_size = 112
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2039906177

    local_members = (
        Member("child", hkpSingleShapeContainer, offset=80, flags=34),
        Member("childSize", _int, offset=96, flags=33),
    )
    members = hkMoppBvTreeShapeBase.members + local_members

    child: hkpSingleShapeContainer
    childSize: _int


class hkpExtendedMeshShapeShapesSubpart(hkpExtendedMeshShapeSubpart):
    alignment = 16
    byte_size = 80
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpExtendedMeshShape::ShapesSubpart"

    local_members = (
        Member("childShapes", hkArray(hkRefPtr(hkpConvexShape, hsh=None), hsh=None), offset=32, flags=32),
        Member("rotation", hkQuaternion, offset=48, flags=34),
        Member("translation", hkVector4, offset=64, flags=34),
    )
    members = hkpExtendedMeshShapeSubpart.members + local_members

    childShapes: list[hkpConvexShape]
    rotation: hkQuaternion
    translation: hkVector4


class hkpExtendedMeshShape(hkpShapeCollection):
    alignment = 16
    byte_size = 320
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 4

    local_members = (
        Member("embeddedTrianglesSubpart", hkpExtendedMeshShapeTrianglesSubpart, offset=48, flags=34),
        Member("aabbHalfExtents", hkVector4, offset=192, flags=32),
        Member("aabbCenter", hkVector4, offset=208, flags=32),
        Member("materialClass", Ptr(hkReflectDetailOpaque, hsh=None), offset=224, flags=33),
        Member("numBitsForSubpartIndex", hkInt32, offset=232, flags=32),
        Member("trianglesSubparts", hkArray(hkpExtendedMeshShapeTrianglesSubpart, hsh=1214306214), offset=240, flags=34),
        Member("shapesSubparts", hkArray(hkpExtendedMeshShapeShapesSubpart, hsh=None), offset=256, flags=34),
        Member("weldingInfo", hkArray(hkUint16, hsh=3551656838), offset=272, flags=32),
        Member("weldingType", hkEnum(hkpWeldingUtilityWeldingType, hkUint8), offset=288, flags=32),
        Member("defaultCollisionFilterInfo", hkUint32, offset=292, flags=32),
        Member("cachedNumChildShapes", hkInt32, offset=296, flags=32),
        Member("triangleRadius", hkReal, offset=300, flags=34),
        Member("padding", hkInt32, offset=304, flags=35),
    )
    members = hkpShapeCollection.members + local_members

    embeddedTrianglesSubpart: hkpExtendedMeshShapeTrianglesSubpart
    aabbHalfExtents: hkVector4
    aabbCenter: hkVector4
    materialClass: hkReflectDetailOpaque
    numBitsForSubpartIndex: hkInt32
    trianglesSubparts: list[hkpExtendedMeshShapeTrianglesSubpart]
    shapesSubparts: list[hkpExtendedMeshShapeShapesSubpart]
    weldingInfo: list[hkUint16]
    weldingType: hkpWeldingUtilityWeldingType
    defaultCollisionFilterInfo: hkUint32
    cachedNumChildShapes: hkInt32
    triangleRadius: hkReal
    padding: hkInt32


class hkpWorldObject(hkReferencedObject):
    alignment = 8
    byte_size = 200
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member("world", Ptr(hkReflectDetailOpaque, hsh=None), offset=16, flags=35),
        Member("userData", hkUlong, offset=24, flags=34),
        Member("collidable", hkpLinkedCollidable, offset=32, flags=34),
        Member("multiThreadCheck", hkMultiThreadCheck, offset=160, flags=34),
        Member("name", hkStringPtr, offset=176, flags=34),
        Member("properties", hkArray(hkSimpleProperty, hsh=None), offset=184, flags=32),
    )
    members = hkReferencedObject.members + local_members

    world: hkReflectDetailOpaque
    userData: hkUlong
    collidable: hkpLinkedCollidable
    multiThreadCheck: hkMultiThreadCheck
    name: hkStringPtr
    properties: list[hkSimpleProperty]


class hkpStorageExtendedMeshShape(hkpExtendedMeshShape):
    alignment = 16
    byte_size = 352
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member("meshstorage", hkArray(Ptr(hkpStorageExtendedMeshShapeMeshSubpartStorage, hsh=502214251), hsh=3469377659), offset=320, flags=34),
        Member("shapestorage", hkArray(Ptr(hkpStorageExtendedMeshShapeShapeSubpartStorage, hsh=None), hsh=None), offset=336, flags=34),
    )
    members = hkpExtendedMeshShape.members + local_members

    meshstorage: list[hkpStorageExtendedMeshShapeMeshSubpartStorage]
    shapestorage: list[hkpStorageExtendedMeshShapeShapeSubpartStorage]


class _CustomParamStorageExtendedMeshShape(hkpStorageExtendedMeshShape):
    alignment = 16
    byte_size = 368
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2448234539
    __real_name = "CustomParamStorageExtendedMeshShape"

    local_members = (
        Member("materialArray", hkArray(Ptr(_CustomMeshParameter, hsh=927471100), hsh=1999126890), offset=352, flags=36),
    )
    members = hkpStorageExtendedMeshShape.members + local_members

    materialArray: list[_CustomMeshParameter]
