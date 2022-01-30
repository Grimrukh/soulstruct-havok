"""Auto-generated types for Havok 2018.

Generated from files:
    skeleton.hkx
    c2180_c.hkx
"""
from __future__ import annotations

from soulstruct_havok.types.core import *


# --- Invalid Types --- #


class hkReflectType(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = 1

    __tag_format_flags = 9
    __real_name = "hkReflect::Type"
    local_members = ()


# --- Primitive Types --- #


class _int(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "int"
    local_members = ()


class _char(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 3

    __tag_format_flags = 9
    __real_name = "char*"
    local_members = ()


class _unsigned_short(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = 16388

    __tag_format_flags = 9
    __real_name = "unsigned short"
    local_members = ()


class _bool(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 8194

    __tag_format_flags = 9
    __real_name = "bool"
    local_members = ()


class _unsigned_char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 8196

    __tag_format_flags = 9
    __real_name = "unsigned char"
    local_members = ()


class _unsigned_int(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 32772

    __tag_format_flags = 9
    __real_name = "unsigned int"
    local_members = ()


class _void(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = 0

    __tag_format_flags = 25
    __abstract_value = 1
    __real_name = "void"
    local_members = ()


class _const_char(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 131

    __tag_format_flags = 9
    __real_name = "const char*"
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
        Member(0, "vec", hkVector4f),
    )
    members = local_members

    vec: hkVector4f


class hkRotationImpl(hkStruct(_float, 12)):
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


class hkMatrix4Impl(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    tag_type_flags = 4136

    __tag_format_flags = 43

    local_members = (
        Member(0, "col0", hkVector4f),
        Member(16, "col1", hkVector4f),
        Member(32, "col2", hkVector4f),
        Member(48, "col3", hkVector4f),
    )
    members = local_members

    col0: hkVector4f
    col1: hkVector4f
    col2: hkVector4f
    col3: hkVector4f

    __templates = (
        TemplateType("tFT", type=_float),
    )


class hkRotationf(hkRotationImpl):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkMatrix4f(hkMatrix4Impl):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkTransformf(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    tag_type_flags = 4136

    __tag_format_flags = 43

    local_members = (
        Member(0, "rotation", hkRotationf, flags=34),
        Member(48, "translation", hkVector4f, flags=34),
    )
    members = local_members

    rotation: hkRotationf
    translation: hkVector4f


class hkMatrix4(hkMatrix4f):
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
    __tag_format_flags = 0
    local_members = ()


# --- Havok Wrappers --- #


class hkUint16(_unsigned_short):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkUintReal(_unsigned_int):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkUint32(_unsigned_int):
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
    tag_type_flags = 131

    __tag_format_flags = 41
    __hsh = 2710609657

    local_members = (
        Member(0, "stringAndFlag", _char, flags=36),
    )
    members = local_members

    stringAndFlag: str


class hkHashMapDetailIndex(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkHashMapDetail::Index"

    local_members = (
        Member(0, "entries", Ptr(_void)),
        Member(8, "hashMod", _int),
    )
    members = local_members

    entries: _void
    hashMod: int


class hkReflectQualifiedType(hkBasePointer):
    alignment = 8
    byte_size = 8
    tag_type_flags = 6

    __tag_format_flags = 43
    __real_name = "hkReflect::QualifiedType"
    _data_type = hkReflectType
    local_members = (
        Member(0, "type", Ptr(hkReflectType), flags=36),
    )
    members = local_members

    type: hkReflectType

    __templates = (
        TemplateType("tTYPE", type=hkReflectType),
    )


class hkPropertyFlagsEnum(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkPropertyFlags::Enum"
    local_members = ()


class hkaSkeletonPartition(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkaSkeleton::Partition"

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "startBoneIndex", hkInt16),
        Member(10, "numBones", hkInt16),
    )
    members = local_members

    name: hkStringPtr
    startBoneIndex: int
    numBones: int


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
        Member(0, "mapping", hkArray(hkInt16, hsh=3571075457)),
    )
    members = local_members

    mapping: list[hkInt16]


class hkBool(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 8194

    __tag_format_flags = 41

    local_members = (
        Member(0, "bool", _char, flags=36),
    )
    members = local_members

    bool: int


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
        Member(0, "time", hkReal),
        Member(8, "text", hkStringPtr),
    )
    members = local_members

    time: float
    text: hkStringPtr


class hkMeshBoneIndexMapping(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "mapping", hkArray(hkInt16, hsh=3571075457)),
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
        Member(0, "vectorData", hkArray(_unsigned_int)),
        Member(16, "floatData", hkArray(_unsigned_int)),
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

    vectorData: list[_unsigned_int]
    floatData: list[_unsigned_int]
    uint32Data: list[hkUint32]
    uint16Data: list[hkUint16]
    uint8Data: list[hkUint8]
    numVerts: int
    vectorStride: int
    floatStride: int
    uint32Stride: int
    uint16Stride: int
    uint8Stride: int


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
        Member(0, "key", hkUint32),
        Member(4, "value", hkUint32),
    )
    members = local_members

    key: int
    value: int


class hkxIndexBufferIndexType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hkxIndexBuffer::IndexType"
    local_members = ()


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


class hclClothDataPlatform(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hclClothData::Platform"
    local_members = ()


class hclSimClothDataOverridableSimulationInfo(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3
    __real_name = "hclSimClothData::OverridableSimulationInfo"

    local_members = (
        Member(0, "gravity", hkVector4),
        Member(16, "globalDampingPerSecond", hkReal),
    )
    members = local_members

    gravity: hkVector4
    globalDampingPerSecond: float


class hclSimClothDataCollidableTransformMap(hk):
    alignment = 8
    byte_size = 40
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclSimClothData::CollidableTransformMap"

    local_members = (
        Member(0, "transformSetIndex", hkInt32),
        Member(8, "transformIndices", hkArray(hkUint32, hsh=1109639201)),
        Member(24, "offsets", hkArray(hkMatrix4, hsh=3899186074)),
    )
    members = local_members

    transformSetIndex: int
    transformIndices: list[hkUint32]
    offsets: list[hkMatrix4]


class hclSimClothDataTransferMotionData(hk):
    alignment = 4
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclSimClothData::TransferMotionData"

    local_members = (
        Member(0, "transformSetIndex", hkUint32),
        Member(4, "transformIndex", hkUint32),
        Member(8, "transferTranslationMotion", hkBool),
        Member(12, "minTranslationSpeed", hkReal),
        Member(16, "maxTranslationSpeed", hkReal),
        Member(20, "minTranslationBlend", hkReal),
        Member(24, "maxTranslationBlend", hkReal),
        Member(28, "transferRotationMotion", hkBool),
        Member(32, "minRotationSpeed", hkReal),
        Member(36, "maxRotationSpeed", hkReal),
        Member(40, "minRotationBlend", hkReal),
        Member(44, "maxRotationBlend", hkReal),
    )
    members = local_members

    transformSetIndex: int
    transformIndex: int
    transferTranslationMotion: bool
    minTranslationSpeed: float
    maxTranslationSpeed: float
    minTranslationBlend: float
    maxTranslationBlend: float
    transferRotationMotion: bool
    minRotationSpeed: float
    maxRotationSpeed: float
    minRotationBlend: float
    maxRotationBlend: float


class hclSimClothDataLandscapeCollisionData(hk):
    alignment = 4
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hclSimClothData::LandscapeCollisionData"

    local_members = (
        Member(0, "landscapeRadius", hkReal),
        Member(4, "enableStuckParticleDetection", hkBool),
        Member(8, "stuckParticlesStretchFactorSq", hkReal),
        Member(12, "pinchDetectionEnabled", hkBool),
        Member(13, "pinchDetectionPriority", hkInt8),
        Member(16, "pinchDetectionRadius", hkReal),
        Member(20, "collisionTolerance", hkReal),
    )
    members = local_members

    landscapeRadius: float
    enableStuckParticleDetection: bool
    stuckParticlesStretchFactorSq: float
    pinchDetectionEnabled: bool
    pinchDetectionPriority: int
    pinchDetectionRadius: float
    collisionTolerance: float


class hclSimClothDataParticleData(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 2467200052
    __version = 2
    __real_name = "hclSimClothData::ParticleData"

    local_members = (
        Member(0, "mass", hkReal),
        Member(4, "invMass", hkReal),
        Member(8, "radius", hkReal),
        Member(12, "friction", hkReal),
    )
    members = local_members

    mass: float
    invMass: float
    radius: float
    friction: float


class hclSimClothDataCollidablePinchingData(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3233440473
    __version = 1
    __real_name = "hclSimClothData::CollidablePinchingData"

    local_members = (
        Member(0, "pinchDetectionEnabled", hkBool),
        Member(1, "pinchDetectionPriority", hkInt8),
        Member(4, "pinchDetectionRadius", hkReal),
    )
    members = local_members

    pinchDetectionEnabled: bool
    pinchDetectionPriority: int
    pinchDetectionRadius: float


class hclVirtualCollisionPointsDataBlock(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::Block"

    local_members = (
        Member(0, "safeDisplacementRadius", hkReal),
        Member(4, "startingVCPIndex", hkUint16),
        Member(6, "numVCPs", hkUint8),
    )
    members = local_members

    safeDisplacementRadius: float
    startingVCPIndex: int
    numVCPs: int


class hclVirtualCollisionPointsDataBarycentricDictionaryEntry(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::BarycentricDictionaryEntry"

    local_members = (
        Member(0, "startingBarycentricIndex", hkUint16),
        Member(2, "numBarycentrics", hkUint8),
    )
    members = local_members

    startingBarycentricIndex: int
    numBarycentrics: int


class hclVirtualCollisionPointsDataBarycentricPair(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::BarycentricPair"

    local_members = (
        Member(0, "u", hkReal),
        Member(4, "v", hkReal),
    )
    members = local_members

    u: float
    v: float


class hclVirtualCollisionPointsDataEdgeFanSection(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::EdgeFanSection"

    local_members = (
        Member(0, "oppositeRealParticleIndex", hkUint16),
        Member(2, "barycentricDictionaryIndex", hkUint16),
    )
    members = local_members

    oppositeRealParticleIndex: int
    barycentricDictionaryIndex: int


class hclVirtualCollisionPointsDataEdgeFan(hk):
    alignment = 2
    byte_size = 6
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::EdgeFan"

    local_members = (
        Member(0, "realParticleIndex", hkUint16),
        Member(2, "edgeStartIndex", hkUint16),
        Member(4, "numEdges", hkUint8),
    )
    members = local_members

    realParticleIndex: int
    edgeStartIndex: int
    numEdges: int


class hclVirtualCollisionPointsDataTriangleFanSection(hk):
    alignment = 2
    byte_size = 6
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::TriangleFanSection"

    local_members = (
        Member(0, "oppositeRealParticleIndices", hkGenericStruct(hkUint16, 2)),
        Member(4, "barycentricDictionaryIndex", hkUint16),
    )
    members = local_members

    oppositeRealParticleIndices: tuple[hkUint16]
    barycentricDictionaryIndex: int


class hclVirtualCollisionPointsDataTriangleFan(hk):
    alignment = 2
    byte_size = 6
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::TriangleFan"

    local_members = (
        Member(0, "realParticleIndex", hkUint16),
        Member(2, "vcpStartIndex", hkUint16),
        Member(4, "numTriangles", hkUint8),
    )
    members = local_members

    realParticleIndex: int
    vcpStartIndex: int
    numTriangles: int


class hclVirtualCollisionPointsDataEdgeFanLandscape(hk):
    alignment = 2
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::EdgeFanLandscape"

    local_members = (
        Member(0, "realParticleIndex", hkUint16),
        Member(2, "edgeStartIndex", hkUint16),
        Member(4, "vcpStartIndex", hkUint16),
        Member(6, "numEdges", hkUint8),
    )
    members = local_members

    realParticleIndex: int
    edgeStartIndex: int
    vcpStartIndex: int
    numEdges: int


class hclVirtualCollisionPointsDataTriangleFanLandscape(hk):
    alignment = 2
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclVirtualCollisionPointsData::TriangleFanLandscape"

    local_members = (
        Member(0, "realParticleIndex", hkUint16),
        Member(2, "triangleStartIndex", hkUint16),
        Member(4, "vcpStartIndex", hkUint16),
        Member(6, "numTriangles", hkUint8),
    )
    members = local_members

    realParticleIndex: int
    triangleStartIndex: int
    vcpStartIndex: int
    numTriangles: int


class hclBufferLayoutTriangleFormat(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hclBufferLayout::TriangleFormat"
    local_members = ()


class hclBufferUsage(hk):
    alignment = 1
    byte_size = 5
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "perComponentFlags", hkGenericStruct(hkUint8, 4)),
        Member(4, "trianglesRead", hkBool),
    )
    members = local_members

    perComponentFlags: tuple[hkUint8]
    trianglesRead: bool


class hkHandle(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "value", hkUint32, flags=34),
    )
    members = local_members

    value: int

    __templates = (
        TemplateType("tTYPE", type=hkUint32),
        TemplateValue("vINVALID_VALUE", value=2147483647),
    )


class hclStateDependencyGraphBranch(hk):
    alignment = 8
    byte_size = 56
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2355611125
    __real_name = "hclStateDependencyGraph::Branch"

    local_members = (
        Member(0, "branchId", _int),
        Member(8, "stateOperatorIndices", hkArray(_int, hsh=910429161)),
        Member(24, "parentBranches", hkArray(_int, hsh=910429161)),
        Member(40, "childBranches", hkArray(_int, hsh=910429161)),
    )
    members = local_members

    branchId: int
    stateOperatorIndices: list[_int]
    parentBranches: list[_int]
    childBranches: list[_int]


class hclStateTransitionSimClothTransitionData(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclStateTransition::SimClothTransitionData"

    local_members = (
        Member(0, "isSimulated", hkBool),
        Member(8, "transitionConstraints", hkArray(hkHandle)),
        Member(24, "transitionType", hkUint32),
    )
    members = local_members

    isSimulated: bool
    transitionConstraints: list[hkHandle]
    transitionType: int


class hclRuntimeConversionInfoVectorConversion(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hclRuntimeConversionInfo::VectorConversion"
    local_members = ()


class hclBufferLayoutSlotFlags(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hclBufferLayout::SlotFlags"
    local_members = ()


class hclBlendSomeVerticesOperatorBlendWeightType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hclBlendSomeVerticesOperator::BlendWeightType"
    local_members = ()


class hclStateTransitionTransitionType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hclStateTransition::TransitionType"
    local_members = ()


class hkBitFieldStorage(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "words", hkArray(hkUint32, hsh=1109639201)),
        Member(16, "numBits", _int),
    )
    members = local_members

    words: list[hkUint32]
    numBits: int

    __templates = (
        TemplateType("tStorage", type=hkArray(hkUint32, hsh=1109639201)),
    )


class hclObjectSpaceDeformerLocalBlockUnpackedPN(hk):
    alignment = 16
    byte_size = 512
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::LocalBlockUnpackedPN"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkVector4, 16)),
        Member(256, "localNormal", hkGenericStruct(hkVector4, 16)),
    )
    members = local_members

    localPosition: tuple[hkVector4]
    localNormal: tuple[hkVector4]


class hclObjectSpaceDeformerEightBlendEntryBlock(hk):
    alignment = 2
    byte_size = 544
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::EightBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 128)),
        Member(288, "boneWeights", hkGenericStruct(hkUint16, 128)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint16]


class hclObjectSpaceDeformerSevenBlendEntryBlock(hk):
    alignment = 2
    byte_size = 480
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::SevenBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 112)),
        Member(256, "boneWeights", hkGenericStruct(hkUint16, 112)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint16]


class hclObjectSpaceDeformerSixBlendEntryBlock(hk):
    alignment = 2
    byte_size = 416
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::SixBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 96)),
        Member(224, "boneWeights", hkGenericStruct(hkUint16, 96)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint16]


class hclObjectSpaceDeformerFiveBlendEntryBlock(hk):
    alignment = 2
    byte_size = 352
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::FiveBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 80)),
        Member(192, "boneWeights", hkGenericStruct(hkUint16, 80)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint16]


class hclObjectSpaceDeformerFourBlendEntryBlock(hk):
    alignment = 2
    byte_size = 224
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 94201665
    __real_name = "hclObjectSpaceDeformer::FourBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 64)),
        Member(160, "boneWeights", hkGenericStruct(hkUint8, 64)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint8]


class hclObjectSpaceDeformerThreeBlendEntryBlock(hk):
    alignment = 2
    byte_size = 176
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3839925180
    __real_name = "hclObjectSpaceDeformer::ThreeBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 48)),
        Member(128, "boneWeights", hkGenericStruct(hkUint8, 48)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint8]


class hclObjectSpaceDeformerTwoBlendEntryBlock(hk):
    alignment = 2
    byte_size = 128
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2865152819
    __real_name = "hclObjectSpaceDeformer::TwoBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 32)),
        Member(96, "boneWeights", hkGenericStruct(hkUint8, 32)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    boneWeights: tuple[hkUint8]


class hclObjectSpaceDeformerOneBlendEntryBlock(hk):
    alignment = 2
    byte_size = 64
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3517680068
    __real_name = "hclObjectSpaceDeformer::OneBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 16)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]


class hkPackedVector3(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "values", hkGenericStruct(hkInt16, 4)),
    )
    members = local_members

    values: tuple[hkInt16]


class hclMoveParticlesOperatorVertexParticlePair(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3905957961
    __real_name = "hclMoveParticlesOperator::VertexParticlePair"

    local_members = (
        Member(0, "vertexIndex", hkUint16),
        Member(2, "particleIndex", hkUint16),
    )
    members = local_members

    vertexIndex: int
    particleIndex: int


class hclSimulateOperatorConfig(hk):
    alignment = 8
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3570302244
    __real_name = "hclSimulateOperator::Config"

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "constraintExecution", hkArray(hkInt32, hsh=1517998030)),
        Member(24, "instanceCollidablesUsed", hkArray(hkBool, hsh=3977017243)),
        Member(40, "subSteps", hkUint8),
        Member(41, "numberOfSolveIterations", hkUint8),
        Member(42, "useAllInstanceCollidables", hkBool),
        Member(43, "adaptConstraintStiffness", hkBool),
    )
    members = local_members

    name: hkStringPtr
    constraintExecution: list[hkInt32]
    instanceCollidablesUsed: list[hkBool]
    subSteps: int
    numberOfSolveIterations: int
    useAllInstanceCollidables: bool
    adaptConstraintStiffness: bool


class hclObjectSpaceDeformerLocalBlockP(hk):
    alignment = 8
    byte_size = 128
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1716201389
    __version = 1
    __real_name = "hclObjectSpaceDeformer::LocalBlockP"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkPackedVector3, 16)),
    )
    members = local_members

    localPosition: tuple[hkPackedVector3]


class hclObjectSpaceDeformerLocalBlockUnpackedP(hk):
    alignment = 16
    byte_size = 256
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::LocalBlockUnpackedP"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkVector4, 16)),
    )
    members = local_members

    localPosition: tuple[hkVector4]


class hclObjectSpaceMeshMeshDeformOperatorScaleNormalBehaviour(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hclObjectSpaceMeshMeshDeformOperator::ScaleNormalBehaviour"
    local_members = ()


class hclObjectSpaceDeformerLocalBlockPNT(hk):
    alignment = 8
    byte_size = 384
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 848274287
    __version = 1
    __real_name = "hclObjectSpaceDeformer::LocalBlockPNT"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkPackedVector3, 16)),
        Member(128, "localNormal", hkGenericStruct(hkPackedVector3, 16)),
        Member(256, "localTangent", hkGenericStruct(hkPackedVector3, 16)),
    )
    members = local_members

    localPosition: tuple[hkPackedVector3]
    localNormal: tuple[hkPackedVector3]
    localTangent: tuple[hkPackedVector3]


class hclObjectSpaceDeformerLocalBlockUnpackedPNT(hk):
    alignment = 16
    byte_size = 768
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclObjectSpaceDeformer::LocalBlockUnpackedPNT"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkVector4, 16)),
        Member(256, "localNormal", hkGenericStruct(hkVector4, 16)),
        Member(512, "localTangent", hkGenericStruct(hkVector4, 16)),
    )
    members = local_members

    localPosition: tuple[hkVector4]
    localNormal: tuple[hkVector4]
    localTangent: tuple[hkVector4]


class hclRuntimeConversionInfoSlotConversion(hk):
    alignment = 1
    byte_size = 7
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclRuntimeConversionInfo::SlotConversion"

    local_members = (
        Member(0, "elements", hkGenericStruct(hkUint8, 4)),
        Member(4, "numElements", hkUint8),
        Member(5, "index", hkUint8),
        Member(6, "partialWrite", hkBool),
    )
    members = local_members

    elements: tuple[hkUint8]
    numElements: int
    index: int
    partialWrite: bool


class hclRuntimeConversionInfoElementConversion(hk):
    alignment = 1
    byte_size = 3
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclRuntimeConversionInfo::ElementConversion"

    local_members = (
        Member(0, "index", hkUint8),
        Member(1, "offset", hkUint8),
        Member(2, "conversion", hkEnum(hclRuntimeConversionInfoVectorConversion, hkUint8)),
    )
    members = local_members

    index: int
    offset: int
    conversion: hclRuntimeConversionInfoVectorConversion


class hclSimpleMeshBoneDeformOperatorTriangleBonePair(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2878957036
    __real_name = "hclSimpleMeshBoneDeformOperator::TriangleBonePair"

    local_members = (
        Member(0, "boneOffset", hkUint16),
        Member(2, "triangleOffset", hkUint16),
    )
    members = local_members

    boneOffset: int
    triangleOffset: int


class hclBoneSpaceDeformerLocalBlockP(hk):
    alignment = 16
    byte_size = 256
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2451926677
    __real_name = "hclBoneSpaceDeformer::LocalBlockP"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkVector4, 16)),
    )
    members = local_members

    localPosition: tuple[hkVector4]


class hclBoneSpaceDeformerLocalBlockUnpackedP(hk):
    alignment = 16
    byte_size = 256
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclBoneSpaceDeformer::LocalBlockUnpackedP"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkVector4, 16)),
    )
    members = local_members

    localPosition: tuple[hkVector4]


class hclBoneSpaceMeshMeshDeformOperatorScaleNormalBehaviour(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hclBoneSpaceMeshMeshDeformOperator::ScaleNormalBehaviour"
    local_members = ()


class hclBoneSpaceDeformerFourBlendEntryBlock(hk):
    alignment = 2
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hclBoneSpaceDeformer::FourBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 4)),
        Member(8, "boneIndices", hkGenericStruct(hkUint16, 16)),
        Member(40, "padding", hkGenericStruct(hkUint8, 8), flags=33),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    padding: tuple[hkUint8]


class hclBoneSpaceDeformerThreeBlendEntryBlock(hk):
    alignment = 2
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hclBoneSpaceDeformer::ThreeBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 5)),
        Member(10, "boneIndices", hkGenericStruct(hkUint16, 15)),
        Member(40, "padding", hkGenericStruct(hkUint8, 8), flags=33),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]
    padding: tuple[hkUint8]


class hclBoneSpaceDeformerTwoBlendEntryBlock(hk):
    alignment = 2
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2640620584
    __real_name = "hclBoneSpaceDeformer::TwoBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 8)),
        Member(16, "boneIndices", hkGenericStruct(hkUint16, 16)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]


class hclBoneSpaceDeformerOneBlendEntryBlock(hk):
    alignment = 2
    byte_size = 64
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2248773505
    __real_name = "hclBoneSpaceDeformer::OneBlendEntryBlock"

    local_members = (
        Member(0, "vertexIndices", hkGenericStruct(hkUint16, 16)),
        Member(32, "boneIndices", hkGenericStruct(hkUint16, 16)),
    )
    members = local_members

    vertexIndices: tuple[hkUint16]
    boneIndices: tuple[hkUint16]


class hclStandardLinkConstraintSetLink(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2334495902
    __real_name = "hclStandardLinkConstraintSet::Link"

    local_members = (
        Member(0, "particleA", hkUint16),
        Member(2, "particleB", hkUint16),
        Member(4, "restLength", hkReal),
        Member(8, "stiffness", hkReal),
    )
    members = local_members

    particleA: int
    particleB: int
    restLength: float
    stiffness: float


class hclStretchLinkConstraintSetLink(hk):
    alignment = 4
    byte_size = 12
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2717653492
    __real_name = "hclStretchLinkConstraintSet::Link"

    local_members = (
        Member(0, "particleA", hkUint16),
        Member(2, "particleB", hkUint16),
        Member(4, "restLength", hkReal),
        Member(8, "stiffness", hkReal),
    )
    members = local_members

    particleA: int
    particleB: int
    restLength: float
    stiffness: float


class hclLocalRangeConstraintSetLocalConstraint(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2381122027
    __real_name = "hclLocalRangeConstraintSet::LocalConstraint"

    local_members = (
        Member(0, "particleIndex", hkUint16),
        Member(2, "referenceVertex", hkUint16),
        Member(4, "maximumDistance", hkReal),
        Member(8, "maxNormalDistance", hkReal),
        Member(12, "minNormalDistance", hkReal),
    )
    members = local_members

    particleIndex: int
    referenceVertex: int
    maximumDistance: float
    maxNormalDistance: float
    minNormalDistance: float


class hclLocalRangeConstraintSetShapeType(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 33284

    __tag_format_flags = 9
    __real_name = "hclLocalRangeConstraintSet::ShapeType"
    local_members = ()


class hclBendStiffnessConstraintSetLink(hk):
    alignment = 4
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 275062867
    __version = 1
    __real_name = "hclBendStiffnessConstraintSet::Link"

    local_members = (
        Member(0, "weightA", hkReal),
        Member(4, "weightB", hkReal),
        Member(8, "weightC", hkReal),
        Member(12, "weightD", hkReal),
        Member(16, "bendStiffness", hkReal),
        Member(20, "restCurvature", hkReal),
        Member(24, "particleA", hkUint16),
        Member(26, "particleB", hkUint16),
        Member(28, "particleC", hkUint16),
        Member(30, "particleD", hkUint16),
    )
    members = local_members

    weightA: float
    weightB: float
    weightC: float
    weightD: float
    bendStiffness: float
    restCurvature: float
    particleA: int
    particleB: int
    particleC: int
    particleD: int


class hclTransitionConstraintSetPerParticle(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1322749721
    __version = 1
    __real_name = "hclTransitionConstraintSet::PerParticle"

    local_members = (
        Member(0, "particleIndex", hkUint16),
        Member(2, "referenceVertex", hkUint16),
        Member(4, "toAnimDelay", hkReal),
        Member(8, "toSimDelay", hkReal),
        Member(12, "toSimMaxDistance", hkReal),
    )
    members = local_members

    particleIndex: int
    referenceVertex: int
    toAnimDelay: float
    toSimDelay: float
    toSimMaxDistance: float


class hkReflectAny(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = 8

    __tag_format_flags = 43
    __real_name = "hkReflect::Any"

    local_members = (
        Member(0, "type", hkReflectQualifiedType, flags=36),
        Member(8, "status", _unsigned_char, flags=36),
        Member(16, "buf", hkGenericStruct(hkUintReal, 4), flags=36),
    )
    members = local_members

    type: hkReflectQualifiedType
    status: int
    buf: tuple[hkUintReal]


class hkFlags(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = 32772

    __tag_format_flags = 41

    local_members = (
        Member(0, "storage", hkUint32, flags=34),
    )
    members = local_members

    storage: int

    __templates = (
        TemplateType("tBITS", type=hkPropertyFlagsEnum),
        TemplateType("tSTORAGE", type=hkUint32),
    )


class hkaBone(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 704422420

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "lockTranslation", hkBool),
    )
    members = local_members

    name: hkStringPtr
    lockTranslation: bool


class hkaAnnotationTrack(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "trackName", hkStringPtr),
        Member(8, "annotations", hkArray(hkaAnnotationTrackAnnotation)),
    )
    members = local_members

    trackName: hkStringPtr
    annotations: list[hkaAnnotationTrackAnnotation]


class hkxVertexDescriptionElementDecl(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

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
    channelID: hkStringPtr


class hkxVertexAnimationUsageMap(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = 7

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


class hclVirtualCollisionPointsData(hk):
    alignment = 8
    byte_size = 304
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "blocks", hkArray(hclVirtualCollisionPointsDataBlock)),
        Member(16, "numVCPoints", hkUint16),
        Member(24, "landscapeParticlesBlockIndex", hkArray(hkUint16, hsh=3431155310)),
        Member(40, "numLandscapeVCPoints", hkUint16),
        Member(48, "edgeBarycentricsDictionary", hkArray(hkReal, hsh=2219021489)),
        Member(64, "edgeDictionaryEntries", hkArray(hclVirtualCollisionPointsDataBarycentricDictionaryEntry)),
        Member(80, "triangleBarycentricsDictionary", hkArray(hclVirtualCollisionPointsDataBarycentricPair)),
        Member(
            96,
            "triangleDictionaryEntries",
            hkArray(hclVirtualCollisionPointsDataBarycentricDictionaryEntry),
        ),
        Member(112, "edges", hkArray(hclVirtualCollisionPointsDataEdgeFanSection)),
        Member(128, "edgeFans", hkArray(hclVirtualCollisionPointsDataEdgeFan)),
        Member(144, "triangles", hkArray(hclVirtualCollisionPointsDataTriangleFanSection)),
        Member(160, "triangleFans", hkArray(hclVirtualCollisionPointsDataTriangleFan)),
        Member(176, "edgesLandscape", hkArray(hclVirtualCollisionPointsDataEdgeFanSection)),
        Member(192, "edgeFansLandscape", hkArray(hclVirtualCollisionPointsDataEdgeFanLandscape)),
        Member(208, "trianglesLandscape", hkArray(hclVirtualCollisionPointsDataTriangleFanSection)),
        Member(224, "triangleFansLandscape", hkArray(hclVirtualCollisionPointsDataTriangleFanLandscape)),
        Member(240, "edgeFanIndices", hkArray(hkUint16, hsh=3431155310)),
        Member(256, "triangleFanIndices", hkArray(hkUint16, hsh=3431155310)),
        Member(272, "edgeFanIndicesLandscape", hkArray(hkUint16, hsh=3431155310)),
        Member(288, "triangleFanIndicesLandscape", hkArray(hkUint16, hsh=3431155310)),
    )
    members = local_members

    blocks: list[hclVirtualCollisionPointsDataBlock]
    numVCPoints: int
    landscapeParticlesBlockIndex: list[hkUint16]
    numLandscapeVCPoints: int
    edgeBarycentricsDictionary: list[hkReal]
    edgeDictionaryEntries: list[hclVirtualCollisionPointsDataBarycentricDictionaryEntry]
    triangleBarycentricsDictionary: list[hclVirtualCollisionPointsDataBarycentricPair]
    triangleDictionaryEntries: list[hclVirtualCollisionPointsDataBarycentricDictionaryEntry]
    edges: list[hclVirtualCollisionPointsDataEdgeFanSection]
    edgeFans: list[hclVirtualCollisionPointsDataEdgeFan]
    triangles: list[hclVirtualCollisionPointsDataTriangleFanSection]
    triangleFans: list[hclVirtualCollisionPointsDataTriangleFan]
    edgesLandscape: list[hclVirtualCollisionPointsDataEdgeFanSection]
    edgeFansLandscape: list[hclVirtualCollisionPointsDataEdgeFanLandscape]
    trianglesLandscape: list[hclVirtualCollisionPointsDataTriangleFanSection]
    triangleFansLandscape: list[hclVirtualCollisionPointsDataTriangleFanLandscape]
    edgeFanIndices: list[hkUint16]
    triangleFanIndices: list[hkUint16]
    edgeFanIndicesLandscape: list[hkUint16]
    triangleFanIndicesLandscape: list[hkUint16]


class hclClothStateBufferAccess(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 746522671
    __version = 2
    __real_name = "hclClothState::BufferAccess"

    local_members = (
        Member(0, "bufferIndex", hkUint32),
        Member(4, "bufferUsage", hclBufferUsage),
        Member(12, "shadowBufferIndex", hkUint32),
    )
    members = local_members

    bufferIndex: int
    bufferUsage: hclBufferUsage
    shadowBufferIndex: int


class hclBufferLayoutBufferElement(hk):
    alignment = 1
    byte_size = 4
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclBufferLayout::BufferElement"

    local_members = (
        Member(0, "vectorConversion", hkEnum(hclRuntimeConversionInfoVectorConversion, hkUint8)),
        Member(1, "vectorSize", hkUint8),
        Member(2, "slotId", hkUint8),
        Member(3, "slotStart", hkUint8),
    )
    members = local_members

    vectorConversion: hclRuntimeConversionInfoVectorConversion
    vectorSize: int
    slotId: int
    slotStart: int


class hclBufferLayoutSlot(hk):
    alignment = 1
    byte_size = 2
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclBufferLayout::Slot"

    local_members = (
        Member(0, "flags", hkEnum(hclBufferLayoutSlotFlags, hkUint8)),
        Member(1, "stride", hkUint8),
    )
    members = local_members

    flags: hclBufferLayoutSlotFlags
    stride: int


class hclStateTransitionBlendOpTransitionData(hk):
    alignment = 8
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclStateTransition::BlendOpTransitionData"

    local_members = (
        Member(0, "bufferASimCloths", hkArray(_int, hsh=910429161)),
        Member(16, "bufferBSimCloths", hkArray(_int, hsh=910429161)),
        Member(32, "transitionType", hkEnum(hclStateTransitionTransitionType, hkUint32)),
        Member(36, "blendWeightType", hclBlendSomeVerticesOperatorBlendWeightType),
        Member(40, "blendOperatorId", _unsigned_int),
    )
    members = local_members

    bufferASimCloths: list[_int]
    bufferBSimCloths: list[_int]
    transitionType: hclStateTransitionTransitionType
    blendWeightType: int
    blendOperatorId: int


class hkBitFieldBase(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "storage", hkBitFieldStorage, flags=34),
    )
    members = local_members

    storage: hkBitFieldStorage

    __templates = (
        TemplateType("tStorage", type=hkBitFieldStorage),
    )


class hclObjectSpaceDeformer(hk):
    alignment = 8
    byte_size = 152
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(0, "eightBlendEntries", hkArray(hclObjectSpaceDeformerEightBlendEntryBlock)),
        Member(16, "sevenBlendEntries", hkArray(hclObjectSpaceDeformerSevenBlendEntryBlock)),
        Member(32, "sixBlendEntries", hkArray(hclObjectSpaceDeformerSixBlendEntryBlock)),
        Member(48, "fiveBlendEntries", hkArray(hclObjectSpaceDeformerFiveBlendEntryBlock)),
        Member(64, "fourBlendEntries", hkArray(hclObjectSpaceDeformerFourBlendEntryBlock, hsh=3126888922)),
        Member(80, "threeBlendEntries", hkArray(hclObjectSpaceDeformerThreeBlendEntryBlock, hsh=407671142)),
        Member(96, "twoBlendEntries", hkArray(hclObjectSpaceDeformerTwoBlendEntryBlock, hsh=1065349417)),
        Member(112, "oneBlendEntries", hkArray(hclObjectSpaceDeformerOneBlendEntryBlock, hsh=2809253903)),
        Member(128, "controlBytes", hkArray(hkUint8, hsh=2331026425)),
        Member(144, "startVertexIndex", hkUint16),
        Member(146, "endVertexIndex", hkUint16),
        Member(148, "partialWrite", hkBool),
    )
    members = local_members

    eightBlendEntries: list[hclObjectSpaceDeformerEightBlendEntryBlock]
    sevenBlendEntries: list[hclObjectSpaceDeformerSevenBlendEntryBlock]
    sixBlendEntries: list[hclObjectSpaceDeformerSixBlendEntryBlock]
    fiveBlendEntries: list[hclObjectSpaceDeformerFiveBlendEntryBlock]
    fourBlendEntries: list[hclObjectSpaceDeformerFourBlendEntryBlock]
    threeBlendEntries: list[hclObjectSpaceDeformerThreeBlendEntryBlock]
    twoBlendEntries: list[hclObjectSpaceDeformerTwoBlendEntryBlock]
    oneBlendEntries: list[hclObjectSpaceDeformerOneBlendEntryBlock]
    controlBytes: list[hkUint8]
    startVertexIndex: int
    endVertexIndex: int
    partialWrite: bool


class hclObjectSpaceDeformerLocalBlockPN(hk):
    alignment = 8
    byte_size = 256
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 934674811
    __version = 1
    __real_name = "hclObjectSpaceDeformer::LocalBlockPN"

    local_members = (
        Member(0, "localPosition", hkGenericStruct(hkPackedVector3, 16)),
        Member(128, "localNormal", hkGenericStruct(hkPackedVector3, 16)),
    )
    members = local_members

    localPosition: tuple[hkPackedVector3]
    localNormal: tuple[hkPackedVector3]


class hclRuntimeConversionInfo(hk):
    alignment = 1
    byte_size = 42
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 0

    local_members = (
        Member(0, "slotConversions", hkGenericStruct(hclRuntimeConversionInfoSlotConversion, 4)),
        Member(28, "elementConversions", hkGenericStruct(hclRuntimeConversionInfoElementConversion, 4)),
        Member(40, "numSlotsConverted", hkUint8),
        Member(41, "numElementsConverted", hkUint8),
    )
    members = local_members

    slotConversions: tuple[hclRuntimeConversionInfoSlotConversion]
    elementConversions: tuple[hclRuntimeConversionInfoElementConversion]
    numSlotsConverted: int
    numElementsConverted: int


class hclBoneSpaceDeformer(hk):
    alignment = 8
    byte_size = 88
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "fourBlendEntries", hkArray(hclBoneSpaceDeformerFourBlendEntryBlock)),
        Member(16, "threeBlendEntries", hkArray(hclBoneSpaceDeformerThreeBlendEntryBlock)),
        Member(32, "twoBlendEntries", hkArray(hclBoneSpaceDeformerTwoBlendEntryBlock, hsh=1493222457)),
        Member(48, "oneBlendEntries", hkArray(hclBoneSpaceDeformerOneBlendEntryBlock, hsh=3238978847)),
        Member(64, "controlBytes", hkArray(hkUint8, hsh=2331026425)),
        Member(80, "startVertexIndex", hkUint16),
        Member(82, "endVertexIndex", hkUint16),
        Member(84, "partialWrite", hkBool),
    )
    members = local_members

    fourBlendEntries: list[hclBoneSpaceDeformerFourBlendEntryBlock]
    threeBlendEntries: list[hclBoneSpaceDeformerThreeBlendEntryBlock]
    twoBlendEntries: list[hclBoneSpaceDeformerTwoBlendEntryBlock]
    oneBlendEntries: list[hclBoneSpaceDeformerOneBlendEntryBlock]
    controlBytes: list[hkUint8]
    startVertexIndex: int
    endVertexIndex: int
    partialWrite: bool


class hkPropertyDesc(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "type", Ptr(hkReflectType)),
        Member(8, "name", _const_char),
        Member(16, "flags", hkFlags),
    )
    members = local_members

    type: hkReflectType
    name: _const_char
    flags: int


class hkxVertexDescription(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "decls", hkArray(hkxVertexDescriptionElementDecl)),
    )
    members = local_members

    decls: list[hkxVertexDescriptionElementDecl]


class hclBufferLayout(hk):
    alignment = 1
    byte_size = 26
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "elementsLayout", hkGenericStruct(hclBufferLayoutBufferElement, 4)),
        Member(16, "slots", hkGenericStruct(hclBufferLayoutSlot, 4)),
        Member(24, "numSlots", hkUint8),
        Member(25, "triangleFormat", hkEnum(hclBufferLayoutTriangleFormat, hkUint8)),
    )
    members = local_members

    elementsLayout: tuple[hclBufferLayoutBufferElement]
    slots: tuple[hclBufferLayoutSlot]
    numSlots: int
    triangleFormat: hclBufferLayoutTriangleFormat


class hclStateTransitionStateTransitionData(hk):
    alignment = 8
    byte_size = 40
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hclStateTransition::StateTransitionData"

    local_members = (
        Member(0, "simClothTransitionData", hkArray(hclStateTransitionSimClothTransitionData)),
        Member(16, "blendOpTransitionData", hkArray(hclStateTransitionBlendOpTransitionData)),
        Member(32, "simulatedState", hkBool),
        Member(33, "emptyState", hkBool),
    )
    members = local_members

    simClothTransitionData: list[hclStateTransitionSimClothTransitionData]
    blendOpTransitionData: list[hclStateTransitionBlendOpTransitionData]
    simulatedState: bool
    emptyState: bool


class hkBitField(hkBitFieldBase):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2
    local_members = ()


class hkPtrAndInt(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 1

    local_members = (
        Member(0, "ptrAndInt", Ptr(hkPropertyDesc), flags=36),
    )
    members = local_members

    ptrAndInt: hkPropertyDesc

    __templates = (
        TemplateType("tPTYPE", type=hkPropertyDesc),
        TemplateType("tITYPE", type=_unsigned_int),
        TemplateValue("vMASK", value=1),
    )


class hclTransformSetUsageTransformTracker(hk):
    alignment = 8
    byte_size = 72
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3022173165
    __real_name = "hclTransformSetUsage::TransformTracker"

    local_members = (
        Member(0, "read", hkBitField),
        Member(24, "readBeforeWrite", hkBitField),
        Member(48, "written", hkBitField),
    )
    members = local_members

    read: hkBitField
    readBeforeWrite: hkBitField
    written: hkBitField


class hkPropertyId(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "desc", hkPtrAndInt, flags=37),
    )
    members = local_members

    desc: hkPtrAndInt


class hkTuple(hk):
    alignment = 16
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "0", hkPropertyId),
        Member(16, "1", hkReflectAny),
    )
    members = local_members

    __templates = (
        TemplateType("tT0", type=hkPropertyId),
        TemplateType("tT1", type=hkReflectAny),
        TemplateType("tT2", type=_void),
        TemplateType("tT3", type=_void),
        TemplateType("tT4", type=_void),
        TemplateType("tT5", type=_void),
        TemplateType("tT6", type=_void),
        TemplateType("tT7", type=_void),
    )


class hclTransformSetUsage(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "perComponentFlags", hkGenericStruct(hkUint8, 2)),
        Member(
            8,
            "perComponentTransformTrackers",
            hkArray(hclTransformSetUsageTransformTracker, hsh=3120187409),
        ),
    )
    members = local_members

    perComponentFlags: tuple[hkUint8]
    perComponentTransformTrackers: list[hclTransformSetUsageTransformTracker]


class hkHashMapDetailMapTuple(hkTuple):
    alignment = 16
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 16
    __real_name = "hkHashMapDetail::MapTuple"
    local_members = ()

    __templates = (
        TemplateType("tKEY", type=hkPropertyId),
        TemplateType("tVALUE", type=hkReflectAny),
    )


class hclClothStateTransformSetAccess(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 951141832
    __real_name = "hclClothState::TransformSetAccess"

    local_members = (
        Member(0, "transformSetIndex", hkUint32),
        Member(8, "transformSetUsage", hclTransformSetUsage),
    )
    members = local_members

    transformSetIndex: int
    transformSetUsage: hclTransformSetUsage


class hkHashBase(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "items", hkArray(hkHashMapDetailMapTuple), flags=34),
        Member(16, "index", hkHashMapDetailIndex, flags=35),
    )
    members = local_members

    items: list[hkHashMapDetailMapTuple]
    index: hkHashMapDetailIndex

    __templates = (
        TemplateType("tITEM", type=hkHashMapDetailMapTuple),
    )


class hkHashMap(hkHashBase):
    alignment = 8
    byte_size = 32
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 16
    local_members = ()

    __templates = (
        TemplateType("tKEY", type=hkPropertyId),
        TemplateType("tVALUE", type=hkReflectAny),
    )


class hkDefaultPropertyBag(hk):
    alignment = 8
    byte_size = 72
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "propertyMap", hkHashMap, flags=34),
        Member(32, "transientPropertyMap", hkHashMap, flags=35),
        Member(64, "locked", _bool, flags=33),
    )
    members = local_members

    propertyMap: hkHashMap
    transientPropertyMap: hkHashMap
    locked: bool


class hkPropertyBag(hkBasePointer):
    alignment = 8
    byte_size = 8
    tag_type_flags = 8

    __tag_format_flags = 43
    _data_type = hkDefaultPropertyBag
    local_members = (
        Member(0, "bag", Ptr(hkDefaultPropertyBag), flags=35),
    )
    members = local_members

    bag: hkDefaultPropertyBag


class hkReferencedObject(hkBaseObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(8, "propertyBag", hkPropertyBag, flags=36),
        Member(16, "memSizeAndFlags", hkUint16, flags=37),
        Member(18, "refCount", hkUint16, flags=37),
    )
    members = hkBaseObject.members + local_members

    propertyBag: hkPropertyBag
    memSizeAndFlags: int
    refCount: int


class hkaBoneAttachment(hkReferencedObject):
    alignment = 16
    byte_size = 128
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(24, "originalSkeletonName", hkStringPtr),
        Member(32, "boneFromAttachment", hkMatrix4),
        Member(96, "attachment", hkRefVariant(hkReferencedObject, hsh=340571500)),
        Member(104, "name", hkStringPtr),
        Member(112, "boneIndex", hkInt16),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: hkStringPtr
    boneFromAttachment: hkMatrix4
    attachment: hkReferencedObject
    name: hkStringPtr
    boneIndex: int


class hkaAnimatedReferenceFrame(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(20, "frameType", hkEnum(hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum, hkInt8), flags=33),
    )
    members = hkReferencedObject.members + local_members

    frameType: hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum


class hkLocalFrame(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3
    local_members = ()


class hkxVertexBuffer(hkReferencedObject):
    alignment = 8
    byte_size = 144
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(24, "data", hkxVertexBufferVertexData, flags=34),
        Member(128, "desc", hkxVertexDescription, flags=34),
    )
    members = hkReferencedObject.members + local_members

    data: hkxVertexBufferVertexData
    desc: hkxVertexDescription


class hkxIndexBuffer(hkReferencedObject):
    alignment = 8
    byte_size = 64
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(20, "indexType", hkEnum(hkxIndexBufferIndexType, hkInt8)),
        Member(24, "indices16", hkArray(hkUint16)),
        Member(40, "indices32", hkArray(hkUint32)),
        Member(56, "vertexBaseOffset", hkUint32),
        Member(60, "length", hkUint32),
    )
    members = hkReferencedObject.members + local_members

    indexType: hkxIndexBufferIndexType
    indices16: list[hkUint16]
    indices32: list[hkUint32]
    vertexBaseOffset: int
    length: int


class hkxVertexAnimation(hkReferencedObject):
    alignment = 8
    byte_size = 200
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 0

    local_members = (
        Member(20, "time", hkReal),
        Member(24, "vertData", hkxVertexBuffer),
        Member(168, "vertexIndexMap", hkArray(hkInt32)),
        Member(184, "componentMap", hkArray(hkxVertexAnimationUsageMap)),
    )
    members = hkReferencedObject.members + local_members

    time: float
    vertData: hkxVertexBuffer
    vertexIndexMap: list[hkInt32]
    componentMap: list[hkxVertexAnimationUsageMap]


class hkxMaterialTextureStage(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkxMaterial::TextureStage"

    local_members = (
        Member(0, "texture", hkRefVariant(hkReferencedObject, hsh=340571500)),
        Member(8, "usageHint", hkEnum(hkxMaterialTextureType, hkInt32)),
        Member(12, "tcoordChannel", hkInt32),
    )
    members = local_members

    texture: hkReferencedObject
    usageHint: hkxMaterialTextureType
    tcoordChannel: int


class hkxAttribute(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "value", hkRefVariant(hkReferencedObject, hsh=340571500)),
    )
    members = local_members

    name: hkStringPtr
    value: hkReferencedObject


class hclShape(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(20, "type", _int, flags=33),
    )
    members = hkReferencedObject.members + local_members

    type: int


class hclBufferDefinition(hkReferencedObject):
    alignment = 8
    byte_size = 80
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 2503985032
    __version = 1

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "type", hkInt32),
        Member(36, "subType", hkInt32),
        Member(40, "numVertices", hkUint32),
        Member(44, "numTriangles", hkUint32),
        Member(48, "bufferLayout", hclBufferLayout),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    type: int
    subType: int
    numVertices: int
    numTriangles: int
    bufferLayout: hclBufferLayout


class hclTransformSetDefinition(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 456237410

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "type", hkInt32),
        Member(36, "numTransforms", hkUint32),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    type: int
    numTransforms: int


class hclOperator(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = 7

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 2

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "operatorID", _unsigned_int),
        Member(36, "type", _unsigned_int, flags=33),
        Member(40, "usedBuffers", hkArray(hclClothStateBufferAccess, hsh=686371003)),
        Member(56, "usedTransformSets", hkArray(hclClothStateTransformSetAccess, hsh=1767586432)),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    operatorID: int
    type: int
    usedBuffers: list[hclClothStateBufferAccess]
    usedTransformSets: list[hclClothStateTransformSetAccess]


class hclStateTransition(hkReferencedObject):
    alignment = 8
    byte_size = 80
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "stateIds", hkArray(hkUint32, hsh=1109639201)),
        Member(48, "stateTransitionData", hkArray(hclStateTransitionStateTransitionData)),
        Member(64, "simClothTransitionConstraints", hkArray(hkArray(hkHandle))),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    stateIds: list[hkUint32]
    stateTransitionData: list[hclStateTransitionStateTransitionData]
    simClothTransitionConstraints: list[list[hkHandle]]


class hclAction(hkReferencedObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3
    local_members = ()


class hclStateDependencyGraph(hkReferencedObject):
    alignment = 8
    byte_size = 96
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2299126301

    local_members = (
        Member(24, "branches", hkArray(hclStateDependencyGraphBranch, hsh=327981087), flags=36),
        Member(40, "rootBranchIds", hkArray(_int, hsh=910429161), flags=36),
        Member(56, "children", hkArray(hkArray(_int, hsh=910429161), hsh=1212383872), flags=36),
        Member(72, "parents", hkArray(hkArray(_int, hsh=910429161), hsh=1212383872), flags=36),
        Member(88, "multiThreadable", hkBool, flags=36),
    )
    members = hkReferencedObject.members + local_members

    branches: list[hclStateDependencyGraphBranch]
    rootBranchIds: list[_int]
    children: list[list[_int]]
    parents: list[list[_int]]
    multiThreadable: bool


class hclSimClothPose(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3477682756

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "positions", hkArray(hkVector4, hsh=1398146255)),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    positions: list[hkVector4]


class hclConstraintSet(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = 7

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "constraintId", hkHandle),
        Member(36, "type", _unsigned_int, flags=35),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    constraintId: hkHandle
    type: int


class hclScratchBufferDefinition(hclBufferDefinition):
    alignment = 8
    byte_size = 104
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2944427578

    local_members = (
        Member(80, "triangleIndices", hkArray(hkUint16, hsh=3431155310)),
        Member(96, "storeNormals", hkBool),
        Member(97, "storeTangentsAndBiTangents", hkBool),
    )
    members = hclBufferDefinition.members + local_members

    triangleIndices: list[hkUint16]
    storeNormals: bool
    storeTangentsAndBiTangents: bool


class hclShadowBufferDefinition(hclBufferDefinition):
    alignment = 8
    byte_size = 104
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 839164263

    local_members = (
        Member(80, "triangleIndices", hkArray(hkUint16, hsh=3431155310)),
        Member(96, "shadowPositions", hkBool),
        Member(97, "shadowNormals", hkBool),
        Member(98, "shadowTangents", hkBool),
        Member(99, "shadowBiTangents", hkBool),
    )
    members = hclBufferDefinition.members + local_members

    triangleIndices: list[hkUint16]
    shadowPositions: bool
    shadowNormals: bool
    shadowTangents: bool
    shadowBiTangents: bool


class hclObjectSpaceSkinOperator(hclOperator):
    alignment = 8
    byte_size = 264
    tag_type_flags = 7

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1

    local_members = (
        Member(72, "boneFromSkinMeshTransforms", hkArray(hkMatrix4, hsh=3899186074)),
        Member(88, "transformSubset", hkArray(hkUint16, hsh=3431155310)),
        Member(104, "outputBufferIndex", hkUint32),
        Member(108, "transformSetIndex", hkUint32),
        Member(112, "objectSpaceDeformer", hclObjectSpaceDeformer),
    )
    members = hclOperator.members + local_members

    boneFromSkinMeshTransforms: list[hkMatrix4]
    transformSubset: list[hkUint16]
    outputBufferIndex: int
    transformSetIndex: int
    objectSpaceDeformer: hclObjectSpaceDeformer


class hclMoveParticlesOperator(hclOperator):
    alignment = 8
    byte_size = 96
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3249942978

    local_members = (
        Member(72, "vertexParticlePairs", hkArray(hclMoveParticlesOperatorVertexParticlePair, hsh=2796431132)),
        Member(88, "simClothIndex", hkUint32),
        Member(92, "refBufferIdx", hkUint32),
    )
    members = hclOperator.members + local_members

    vertexParticlePairs: list[hclMoveParticlesOperatorVertexParticlePair]
    simClothIndex: int
    refBufferIdx: int


class hclSimulateOperator(hclOperator):
    alignment = 8
    byte_size = 96
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1931677792
    __version = 4

    local_members = (
        Member(72, "simClothIndex", hkUint32),
        Member(80, "simulateOpConfigs", hkArray(hclSimulateOperatorConfig, hsh=137221530)),
    )
    members = hclOperator.members + local_members

    simClothIndex: int
    simulateOpConfigs: list[hclSimulateOperatorConfig]


class hclObjectSpaceMeshMeshDeformOperator(hclOperator):
    alignment = 8
    byte_size = 280
    tag_type_flags = 7

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 1

    local_members = (
        Member(72, "inputBufferIdx", hkUint32),
        Member(76, "outputBufferIdx", hkUint32),
        Member(
            80,
            "scaleNormalBehaviour",
            hkEnum(hclObjectSpaceMeshMeshDeformOperatorScaleNormalBehaviour, hkUint32),
        ),
        Member(88, "inputTrianglesSubset", hkArray(hkUint16, hsh=3431155310)),
        Member(104, "triangleFromMeshTransforms", hkArray(hkMatrix4, hsh=3899186074)),
        Member(120, "objectSpaceDeformer", hclObjectSpaceDeformer),
        Member(272, "customSkinDeform", hkBool),
    )
    members = hclOperator.members + local_members

    inputBufferIdx: int
    outputBufferIdx: int
    scaleNormalBehaviour: hclObjectSpaceMeshMeshDeformOperatorScaleNormalBehaviour
    inputTrianglesSubset: list[hkUint16]
    triangleFromMeshTransforms: list[hkMatrix4]
    objectSpaceDeformer: hclObjectSpaceDeformer
    customSkinDeform: bool


class hclUpdateAllVertexFramesOperator(hclOperator):
    alignment = 8
    byte_size = 184
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3765729381
    __version = 3

    local_members = (
        Member(72, "vertToNormalID", hkArray(hkUint16, hsh=3431155310)),
        Member(88, "triangleFlips", hkArray(hkUint8, hsh=2331026425)),
        Member(104, "referenceVertices", hkArray(hkUint16, hsh=3431155310)),
        Member(120, "tangentEdgeCosAngle", hkArray(hkReal, hsh=2219021489)),
        Member(136, "tangentEdgeSinAngle", hkArray(hkReal, hsh=2219021489)),
        Member(152, "biTangentFlip", hkArray(hkReal, hsh=2219021489)),
        Member(168, "bufferIdx", hkUint32),
        Member(172, "numUniqueNormalIDs", hkUint32),
        Member(176, "updateNormals", hkBool),
        Member(177, "updateTangents", hkBool),
        Member(178, "updateBiTangents", hkBool),
    )
    members = hclOperator.members + local_members

    vertToNormalID: list[hkUint16]
    triangleFlips: list[hkUint8]
    referenceVertices: list[hkUint16]
    tangentEdgeCosAngle: list[hkReal]
    tangentEdgeSinAngle: list[hkReal]
    biTangentFlip: list[hkReal]
    bufferIdx: int
    numUniqueNormalIDs: int
    updateNormals: bool
    updateTangents: bool
    updateBiTangents: bool


class hclObjectSpaceSkinPNTOperator(hclObjectSpaceSkinOperator):
    alignment = 8
    byte_size = 296
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3245113506
    __version = 1

    local_members = (
        Member(264, "localPNTs", hkArray(hclObjectSpaceDeformerLocalBlockPNT, hsh=3862559966)),
        Member(280, "localUnpackedPNTs", hkArray(hclObjectSpaceDeformerLocalBlockUnpackedPNT)),
    )
    members = hclObjectSpaceSkinOperator.members + local_members

    localPNTs: list[hclObjectSpaceDeformerLocalBlockPNT]
    localUnpackedPNTs: list[hclObjectSpaceDeformerLocalBlockUnpackedPNT]


class hclGatherAllVerticesOperator(hclOperator):
    alignment = 8
    byte_size = 104
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1253355578
    __version = 1

    local_members = (
        Member(72, "vertexInputFromVertexOutput", hkArray(hkInt16, hsh=3571075457)),
        Member(88, "inputBufferIdx", hkUint32),
        Member(92, "outputBufferIdx", hkUint32),
        Member(96, "gatherNormals", hkBool),
        Member(97, "partialGather", hkBool),
    )
    members = hclOperator.members + local_members

    vertexInputFromVertexOutput: list[hkInt16]
    inputBufferIdx: int
    outputBufferIdx: int
    gatherNormals: bool
    partialGather: bool


class hclInputConvertOperator(hclOperator):
    alignment = 8
    byte_size = 128
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 4049141843

    local_members = (
        Member(72, "userBufferIndex", hkUint32),
        Member(76, "shadowBufferIndex", hkUint32),
        Member(80, "conversionInfo", hclRuntimeConversionInfo),
    )
    members = hclOperator.members + local_members

    userBufferIndex: int
    shadowBufferIndex: int
    conversionInfo: hclRuntimeConversionInfo


class hclOutputConvertOperator(hclOperator):
    alignment = 8
    byte_size = 128
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 3763320081

    local_members = (
        Member(72, "userBufferIndex", hkUint32),
        Member(76, "shadowBufferIndex", hkUint32),
        Member(80, "conversionInfo", hclRuntimeConversionInfo),
    )
    members = hclOperator.members + local_members

    userBufferIndex: int
    shadowBufferIndex: int
    conversionInfo: hclRuntimeConversionInfo


class hclSimpleMeshBoneDeformOperator(hclOperator):
    alignment = 8
    byte_size = 112
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2605270853

    local_members = (
        Member(72, "inputBufferIdx", hkUint32),
        Member(76, "outputTransformSetIdx", hkUint32),
        Member(
            80,
            "triangleBonePairs",
            hkArray(hclSimpleMeshBoneDeformOperatorTriangleBonePair, hsh=121283141),
        ),
        Member(96, "localBoneTransforms", hkArray(hkMatrix4, hsh=3899186074)),
    )
    members = hclOperator.members + local_members

    inputBufferIdx: int
    outputTransformSetIdx: int
    triangleBonePairs: list[hclSimpleMeshBoneDeformOperatorTriangleBonePair]
    localBoneTransforms: list[hkMatrix4]


class hclCopyVerticesOperator(hclOperator):
    alignment = 8
    byte_size = 96
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2019478703

    local_members = (
        Member(72, "inputBufferIdx", hkUint32),
        Member(76, "outputBufferIdx", hkUint32),
        Member(80, "numberOfVertices", hkUint32),
        Member(84, "startVertexIn", hkUint32),
        Member(88, "startVertexOut", hkUint32),
        Member(92, "copyNormals", hkBool),
    )
    members = hclOperator.members + local_members

    inputBufferIdx: int
    outputBufferIdx: int
    numberOfVertices: int
    startVertexIn: int
    startVertexOut: int
    copyNormals: bool


class hclBoneSpaceMeshMeshDeformOperator(hclOperator):
    alignment = 8
    byte_size = 192
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(72, "inputBufferIdx", hkUint32),
        Member(76, "outputBufferIdx", hkUint32),
        Member(
            80,
            "scaleNormalBehaviour",
            hkEnum(hclBoneSpaceMeshMeshDeformOperatorScaleNormalBehaviour, hkUint32),
        ),
        Member(88, "inputTrianglesSubset", hkArray(hkUint16, hsh=3431155310)),
        Member(104, "boneSpaceDeformer", hclBoneSpaceDeformer),
    )
    members = hclOperator.members + local_members

    inputBufferIdx: int
    outputBufferIdx: int
    scaleNormalBehaviour: hclBoneSpaceMeshMeshDeformOperatorScaleNormalBehaviour
    inputTrianglesSubset: list[hkUint16]
    boneSpaceDeformer: hclBoneSpaceDeformer


class hclStandardLinkConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 56
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 4078551462

    local_members = (
        Member(40, "links", hkArray(hclStandardLinkConstraintSetLink, hsh=1647365312)),
    )
    members = hclConstraintSet.members + local_members

    links: list[hclStandardLinkConstraintSetLink]


class hclStretchLinkConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 56
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2665167600

    local_members = (
        Member(40, "links", hkArray(hclStretchLinkConstraintSetLink, hsh=4260047912)),
    )
    members = hclConstraintSet.members + local_members

    links: list[hclStretchLinkConstraintSetLink]


class hclLocalRangeConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 72
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3497046835
    __version = 3

    local_members = (
        Member(40, "localConstraints", hkArray(hclLocalRangeConstraintSetLocalConstraint, hsh=2932720944)),
        Member(56, "referenceMeshBufferIdx", hkUint32),
        Member(60, "stiffness", hkReal),
        Member(64, "shapeType", hkEnum(hclLocalRangeConstraintSetShapeType, hkUint32)),
        Member(68, "applyNormalComponent", hkBool),
    )
    members = hclConstraintSet.members + local_members

    localConstraints: list[hclLocalRangeConstraintSetLocalConstraint]
    referenceMeshBufferIdx: int
    stiffness: float
    shapeType: hclLocalRangeConstraintSetShapeType
    applyNormalComponent: bool


class hclBendStiffnessConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 64
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1747957381
    __version = 2

    local_members = (
        Member(40, "links", hkArray(hclBendStiffnessConstraintSetLink, hsh=1918745169)),
        Member(56, "maxRestPoseHeightSq", hkReal),
        Member(60, "clampBendStiffness", hkBool),
        Member(61, "useRestPoseConfig", hkBool),
    )
    members = hclConstraintSet.members + local_members

    links: list[hclBendStiffnessConstraintSetLink]
    maxRestPoseHeightSq: float
    clampBendStiffness: bool
    useRestPoseConfig: bool


class hclTransitionConstraintSet(hclConstraintSet):
    alignment = 8
    byte_size = 80
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 42297855
    __version = 1

    local_members = (
        Member(40, "perParticleData", hkArray(hclTransitionConstraintSetPerParticle, hsh=2562328436)),
        Member(56, "toAnimPeriod", hkReal),
        Member(60, "toAnimPlusDelayPeriod", hkReal),
        Member(64, "toSimPeriod", hkReal),
        Member(68, "toSimPlusDelayPeriod", hkReal),
        Member(72, "referenceMeshBufferIdx", hkUint32),
    )
    members = hclConstraintSet.members + local_members

    perParticleData: list[hclTransitionConstraintSetPerParticle]
    toAnimPeriod: float
    toAnimPlusDelayPeriod: float
    toSimPeriod: float
    toSimPlusDelayPeriod: float
    referenceMeshBufferIdx: int


class hclTaperedCapsuleShape(hclShape):
    alignment = 16
    byte_size = 176
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3051345063
    __version = 2

    local_members = (
        Member(32, "small", hkVector4, flags=34),
        Member(48, "big", hkVector4, flags=34),
        Member(64, "coneApex", hkVector4, flags=34),
        Member(80, "coneAxis", hkVector4, flags=34),
        Member(96, "lVec", hkVector4, flags=34),
        Member(112, "dVec", hkVector4, flags=34),
        Member(128, "tanThetaVecNeg", hkVector4, flags=34),
        Member(144, "smallRadius", hkReal, flags=34),
        Member(148, "bigRadius", hkReal, flags=34),
        Member(152, "l", hkReal, flags=34),
        Member(156, "d", hkReal, flags=34),
        Member(160, "cosTheta", hkReal, flags=34),
        Member(164, "sinTheta", hkReal, flags=34),
        Member(168, "tanTheta", hkReal, flags=34),
        Member(172, "tanThetaSqr", hkReal, flags=34),
    )
    members = hclShape.members + local_members

    small: hkVector4
    big: hkVector4
    coneApex: hkVector4
    coneAxis: hkVector4
    lVec: hkVector4
    dVec: hkVector4
    tanThetaVecNeg: hkVector4
    smallRadius: float
    bigRadius: float
    l: float
    d: float
    cosTheta: float
    sinTheta: float
    tanTheta: float
    tanThetaSqr: float


class hclCapsuleShape(hclShape):
    alignment = 16
    byte_size = 96
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 2376887643
    __version = 1

    local_members = (
        Member(32, "start", hkVector4, flags=34),
        Member(48, "end", hkVector4, flags=34),
        Member(64, "dir", hkVector4, flags=34),
        Member(80, "radius", hkReal, flags=34),
        Member(84, "capLenSqrdInv", hkReal, flags=34),
    )
    members = hclShape.members + local_members

    start: hkVector4
    end: hkVector4
    dir: hkVector4
    radius: float
    capLenSqrdInv: float


class hkRootLevelContainerNamedVariant(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 189790448
    __version = 1
    __real_name = "hkRootLevelContainer::NamedVariant"

    local_members = (
        Member(0, "name", hkStringPtr, flags=36),
        Member(8, "className", hkStringPtr, flags=36),
        Member(16, "variant", hkRefVariant(hkReferencedObject, hsh=340571500), flags=36),
    )
    members = local_members

    name: hkStringPtr
    className: hkStringPtr
    variant: hkReferencedObject


class hkaAnimation(hkReferencedObject):
    alignment = 8
    byte_size = 64
    tag_type_flags = 7

    __tag_format_flags = 61
    __abstract_value = 3
    __version = 3

    local_members = (
        Member(20, "type", hkEnum(hkaAnimationAnimationType, hkInt32), flags=34),
        Member(24, "duration", hkReal),
        Member(28, "numberOfTransformTracks", _int),
        Member(32, "numberOfFloatTracks", _int),
        Member(40, "extractedMotion", hkRefPtr(hkaAnimatedReferenceFrame), flags=34),
        Member(48, "annotationTracks", hkArray(hkaAnnotationTrack)),
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
    byte_size = 96
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(24, "originalSkeletonName", hkStringPtr),
        Member(32, "animation", hkRefPtr(hkaAnimation)),
        Member(40, "transformTrackToBoneIndices", hkArray(hkInt16, hsh=3571075457)),
        Member(56, "floatTrackToFloatSlotIndices", hkArray(hkInt16, hsh=3571075457)),
        Member(72, "partitionIndices", hkArray(hkInt16, hsh=3571075457)),
        Member(88, "blendHint", hkEnum(hkaAnimationBindingBlendHint, hkInt8)),
    )
    members = hkReferencedObject.members + local_members

    originalSkeletonName: hkStringPtr
    animation: hkaAnimation
    transformTrackToBoneIndices: list[hkInt16]
    floatTrackToFloatSlotIndices: list[hkInt16]
    partitionIndices: list[hkInt16]
    blendHint: hkaAnimationBindingBlendHint


class hkaSkeletonLocalFrameOnBone(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkaSkeleton::LocalFrameOnBone"

    local_members = (
        Member(0, "localFrame", hkRefPtr(hkLocalFrame)),
        Member(8, "boneIndex", hkInt16),
    )
    members = local_members

    localFrame: hkLocalFrame
    boneIndex: int


class hkxAttributeGroup(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = 7

    __tag_format_flags = 41

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "attributes", hkArray(hkxAttribute)),
    )
    members = local_members

    name: hkStringPtr
    attributes: list[hkxAttribute]


class hclCollidable(hkReferencedObject):
    alignment = 16
    byte_size = 160
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 4288064896
    __version = 4

    local_members = (
        Member(32, "transform", hkTransform),
        Member(96, "linearVelocity", hkVector4),
        Member(112, "angularVelocity", hkVector4),
        Member(128, "userData", hkUint64),
        Member(136, "shape", Ptr(hclShape, hsh=849809137)),
        Member(144, "name", hkStringPtr),
        Member(152, "pinchDetectionRadius", hkReal),
        Member(156, "pinchDetectionPriority", hkInt8),
        Member(157, "pinchDetectionEnabled", hkBool),
        Member(158, "virtualCollisionPointCollisionEnabled", hkBool),
        Member(159, "enabled", hkBool),
    )
    members = hkReferencedObject.members + local_members

    transform: hkTransform
    linearVelocity: hkVector4
    angularVelocity: hkVector4
    userData: int
    shape: hclShape
    name: hkStringPtr
    pinchDetectionRadius: float
    pinchDetectionPriority: int
    pinchDetectionEnabled: bool
    virtualCollisionPointCollisionEnabled: bool
    enabled: bool


class hclSimClothData(hkReferencedObject):
    alignment = 16
    byte_size = 736
    tag_type_flags = 7

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
    fixedParticles: list[hkUint16]
    doNormals: bool
    simOpIds: list[_unsigned_int]
    simClothPoses: list[hclSimClothPose]
    staticConstraintSets: list[hclConstraintSet]
    antiPinchConstraintSets: list[hclConstraintSet]
    collidableTransformMap: hclSimClothDataCollidableTransformMap
    perInstanceCollidables: list[hclCollidable]
    maxParticleRadius: float
    staticCollisionMasks: list[hkUint32]
    actions: list[hclAction]
    totalMass: float
    transferMotionData: hclSimClothDataTransferMotionData
    transferMotionEnabled: bool
    landscapeCollisionEnabled: bool
    landscapeCollisionData: hclSimClothDataLandscapeCollisionData
    numLandscapeCollidableParticles: int
    triangleIndices: list[hkUint16]
    triangleFlips: list[hkUint8]
    pinchDetectionEnabled: bool
    perParticlePinchDetectionEnabledFlags: list[hkBool]
    collidablePinchingDatas: list[hclSimClothDataCollidablePinchingData]
    minPinchedParticleIndex: int
    maxPinchedParticleIndex: int
    maxCollisionPairs: int
    virtualCollisionPointsData: hclVirtualCollisionPointsData


class hclClothState(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3225525304
    __version = 2

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "operators", hkArray(hkUint32, hsh=1109639201)),
        Member(48, "usedBuffers", hkArray(hclClothStateBufferAccess, hsh=686371003)),
        Member(64, "usedTransformSets", hkArray(hclClothStateTransformSetAccess, hsh=1767586432)),
        Member(80, "usedSimCloths", hkArray(hkUint32, hsh=1109639201)),
        Member(96, "dependencyGraph", Ptr(hclStateDependencyGraph, hsh=1428167545)),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    operators: list[hkUint32]
    usedBuffers: list[hclClothStateBufferAccess]
    usedTransformSets: list[hclClothStateTransformSetAccess]
    usedSimCloths: list[hkUint32]
    dependencyGraph: hclStateDependencyGraph


class hclObjectSpaceSkinPNOperator(hclObjectSpaceSkinOperator):
    alignment = 8
    byte_size = 296
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3646506320
    __version = 1

    local_members = (
        Member(264, "localPNs", hkArray(hclObjectSpaceDeformerLocalBlockPN, hsh=4080327730)),
        Member(280, "localUnpackedPNs", hkArray(hclObjectSpaceDeformerLocalBlockUnpackedPN)),
    )
    members = hclObjectSpaceSkinOperator.members + local_members

    localPNs: list[hclObjectSpaceDeformerLocalBlockPN]
    localUnpackedPNs: list[hclObjectSpaceDeformerLocalBlockUnpackedPN]


class hclObjectSpaceMeshMeshDeformPOperator(hclObjectSpaceMeshMeshDeformOperator):
    alignment = 8
    byte_size = 312
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 48181339
    __version = 1

    local_members = (
        Member(280, "localPs", hkArray(hclObjectSpaceDeformerLocalBlockP, hsh=2974961463)),
        Member(296, "localUnpackedPs", hkArray(hclObjectSpaceDeformerLocalBlockUnpackedP)),
    )
    members = hclObjectSpaceMeshMeshDeformOperator.members + local_members

    localPs: list[hclObjectSpaceDeformerLocalBlockP]
    localUnpackedPs: list[hclObjectSpaceDeformerLocalBlockUnpackedP]


class hclBoneSpaceMeshMeshDeformPOperator(hclBoneSpaceMeshMeshDeformOperator):
    alignment = 8
    byte_size = 224
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1671229033
    __version = 1

    local_members = (
        Member(192, "localPs", hkArray(hclBoneSpaceDeformerLocalBlockP, hsh=2181080418)),
        Member(208, "localUnpackedPs", hkArray(hclBoneSpaceDeformerLocalBlockUnpackedP)),
    )
    members = hclBoneSpaceMeshMeshDeformOperator.members + local_members

    localPs: list[hclBoneSpaceDeformerLocalBlockP]
    localUnpackedPs: list[hclBoneSpaceDeformerLocalBlockUnpackedP]


class hkRootLevelContainer(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = 7

    __tag_format_flags = 41
    __hsh = 2700707004

    local_members = (
        Member(0, "namedVariants", hkArray(hkRootLevelContainerNamedVariant, hsh=2159475074)),
    )
    members = local_members

    namedVariants: list[hkRootLevelContainerNamedVariant]


class hkaSkeleton(hkReferencedObject):
    alignment = 8
    byte_size = 144
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 1663626346
    __version = 6

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "parentIndices", hkArray(hkInt16, hsh=3571075457)),
        Member(48, "bones", hkArray(hkaBone, hsh=2644325209)),
        Member(64, "referencePose", hkArray(hkQsTransform, hsh=2077323384)),
        Member(80, "referenceFloats", hkArray(hkReal)),
        Member(96, "floatSlots", hkArray(hkStringPtr)),
        Member(112, "localFrames", hkArray(hkaSkeletonLocalFrameOnBone)),
        Member(128, "partitions", hkArray(hkaSkeletonPartition)),
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


class hkxAttributeHolder(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(24, "attributeGroups", hkArray(hkxAttributeGroup)),
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
        Member(40, "name", hkStringPtr),
        Member(48, "stages", hkArray(hkxMaterialTextureStage)),
        Member(64, "diffuseColor", hkVector4),
        Member(80, "ambientColor", hkVector4),
        Member(96, "specularColor", hkVector4),
        Member(112, "emissiveColor", hkVector4),
        Member(128, "subMaterials", hkArray(hkRefPtr(DefType("hkxMaterial", lambda: hkxMaterial)))),
        Member(144, "extraData", hkRefVariant(hkReferencedObject, hsh=340571500)),
        Member(152, "uvMapScale", hkGenericStruct(hkReal, 2)),
        Member(160, "uvMapOffset", hkGenericStruct(hkReal, 2)),
        Member(168, "uvMapRotation", hkReal),
        Member(172, "uvMapAlgorithm", hkEnum(hkxMaterialUVMappingAlgorithm, hkUint32)),
        Member(176, "specularMultiplier", hkReal),
        Member(180, "specularExponent", hkReal),
        Member(184, "transparency", hkEnum(hkxMaterialTransparency, hkUint8)),
        Member(192, "userData", hkUlong),
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
    uvMapScale: tuple[hkReal]
    uvMapOffset: tuple[hkReal]
    uvMapRotation: float
    uvMapAlgorithm: hkxMaterialUVMappingAlgorithm
    specularMultiplier: float
    specularExponent: float
    transparency: hkxMaterialTransparency
    userData: int
    properties: list[hkxMaterialProperty]


class hclClothData(hkReferencedObject):
    alignment = 8
    byte_size = 152
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 3963035682
    __version = 3

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "simClothDatas", hkArray(Ptr(hclSimClothData, hsh=2357115667), hsh=3501181651)),
        Member(48, "bufferDefinitions", hkArray(Ptr(hclBufferDefinition, hsh=78898278), hsh=2006368910)),
        Member(
            64,
            "transformSetDefinitions",
            hkArray(Ptr(hclTransformSetDefinition, hsh=360203306), hsh=3317004341),
        ),
        Member(80, "operators", hkArray(Ptr(hclOperator, hsh=2743151593), hsh=2934719668)),
        Member(96, "clothStateDatas", hkArray(Ptr(hclClothState, hsh=372743206), hsh=251459129)),
        Member(112, "stateTransitions", hkArray(Ptr(hclStateTransition))),
        Member(128, "actions", hkArray(Ptr(hclAction))),
        Member(144, "targetPlatform", hkEnum(hclClothDataPlatform, hkUint32)),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    simClothDatas: list[hclSimClothData]
    bufferDefinitions: list[hclBufferDefinition]
    transformSetDefinitions: list[hclTransformSetDefinition]
    operators: list[hclOperator]
    clothStateDatas: list[hclClothState]
    stateTransitions: list[hclStateTransition]
    actions: list[hclAction]
    targetPlatform: hclClothDataPlatform


class hkxMeshSection(hkReferencedObject):
    alignment = 8
    byte_size = 120
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member(24, "vertexBuffer", hkRefPtr(hkxVertexBuffer)),
        Member(32, "indexBuffers", hkArray(hkRefPtr(hkxIndexBuffer))),
        Member(48, "material", hkRefPtr(hkxMaterial)),
        Member(56, "userChannels", hkArray(hkRefVariant(hkReferencedObject, hsh=340571500))),
        Member(72, "vertexAnimations", hkArray(hkRefPtr(hkxVertexAnimation))),
        Member(88, "linearKeyFrameHints", hkArray(_float)),
        Member(104, "boneMatrixMap", hkArray(hkMeshBoneIndexMapping)),
    )
    members = hkReferencedObject.members + local_members

    vertexBuffer: hkxVertexBuffer
    indexBuffers: list[hkxIndexBuffer]
    material: hkxMaterial
    userChannels: list[hkReferencedObject]
    vertexAnimations: list[hkxVertexAnimation]
    linearKeyFrameHints: list[_float]
    boneMatrixMap: list[hkMeshBoneIndexMapping]


class hkxMeshUserChannelInfo(hkxAttributeHolder):
    alignment = 8
    byte_size = 56
    tag_type_flags = 7

    __tag_format_flags = 41
    __real_name = "hkxMesh::UserChannelInfo"

    local_members = (
        Member(40, "name", hkStringPtr),
        Member(48, "className", hkStringPtr),
    )
    members = hkxAttributeHolder.members + local_members

    name: hkStringPtr
    className: hkStringPtr


class hclClothContainer(hkReferencedObject):
    alignment = 8
    byte_size = 56
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 829381375
    __version = 1

    local_members = (
        Member(24, "collidables", hkArray(hkRefPtr(hclCollidable))),
        Member(40, "clothDatas", hkArray(hkRefPtr(hclClothData, hsh=1749100557), hsh=1122004664)),
    )
    members = hkReferencedObject.members + local_members

    collidables: list[hclCollidable]
    clothDatas: list[hclClothData]


class hkxMesh(hkReferencedObject):
    alignment = 8
    byte_size = 56
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(24, "sections", hkArray(hkRefPtr(hkxMeshSection))),
        Member(40, "userChannelInfos", hkArray(hkRefPtr(hkxMeshUserChannelInfo))),
    )
    members = hkReferencedObject.members + local_members

    sections: list[hkxMeshSection]
    userChannelInfos: list[hkxMeshUserChannelInfo]


class hkaMeshBinding(hkReferencedObject):
    alignment = 8
    byte_size = 88
    tag_type_flags = 7

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(24, "mesh", hkRefPtr(hkxMesh)),
        Member(32, "originalSkeletonName", hkStringPtr),
        Member(40, "name", hkStringPtr),
        Member(48, "skeleton", hkRefPtr(hkaSkeleton, hsh=3659816570)),
        Member(56, "mappings", hkArray(hkaMeshBindingMapping)),
        Member(72, "boneFromSkinMeshTransforms", hkArray(hkTransform)),
    )
    members = hkReferencedObject.members + local_members

    mesh: hkxMesh
    originalSkeletonName: hkStringPtr
    name: hkStringPtr
    skeleton: hkaSkeleton
    mappings: list[hkaMeshBindingMapping]
    boneFromSkinMeshTransforms: list[hkTransform]


class hkaAnimationContainer(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = 7

    __tag_format_flags = 45
    __hsh = 2343308884
    __version = 1

    local_members = (
        Member(24, "skeletons", hkArray(hkRefPtr(hkaSkeleton, hsh=3659816570), hsh=1926479907)),
        Member(40, "animations", hkArray(hkRefPtr(hkaAnimation))),
        Member(56, "bindings", hkArray(hkRefPtr(hkaAnimationBinding))),
        Member(72, "attachments", hkArray(hkRefPtr(hkaBoneAttachment))),
        Member(88, "skins", hkArray(hkRefPtr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]
