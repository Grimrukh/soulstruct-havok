"""Havok 2018 core types."""
from __future__ import annotations

__all__ = [
    # hk
    "hk",
    "HK_TYPE",
    "TemplateType",
    "TemplateValue",
    "Member",
    "Interface",
    "DefType",

    # base
    "hkBasePointer",
    "hkContainerHeapAllocator",
    "Ptr_",
    "hkReflectQualifiedType_",
    "hkRefPtr_",
    "hkRefVariant_",
    "hkViewPtr_",
    "hkRelArray_",
    "hkArray_",
    "hkEnum_",
    "hkStruct_",
    "hkFreeListArray_",
    "hkFlags_",

    # 64-bit factory functions
    "Ptr",
    "hkRefPtr",
    "hkRefVariant",
    "hkArray",
    "SimpleArray",
    "hkViewPtr",
    "hkRelArray",
    "hkEnum",
    "hkStruct",
    "hkGenericStruct",
    "hkFreeListArrayElement",
    "hkFreeListArray",
    "hkFlags",

    # hk2018
    "Vector4",
    "hkReflectDetailOpaque",
    "_bool",
    "_int",
    "_const_charSTAR",
    "_unsigned_short",
    "_char",
    "_charSTAR",
    "_float",
    "_short",
    "_signed_char",
    "_unsigned_long_long",
    "_unsigned_int",
    "_unsigned_char",
    "_void",
    "hkVector4f",
    "hkQuaternionf",
    "hkRotationImpl",
    "hkVector4",
    "hkMatrix3Impl",
    "hkMatrix4f",
    "hkRotationf",
    "hkMatrix3f",
    "hkMatrix4Impl",
    "hkMatrix4",
    "hkTransformf",
    "hkMatrix3",
    "hkTransform",
    "hkQsTransformf",
    "hkQsTransform",
    "hkUint32",
    "hkQuaternion",
    "hkUint16",
    "hkReal",
    "hkInt16",
    "hkInt32",
    "hkInt8",
    "hkUlong",
    "hkUint8",
    "hkUint64",
    "hkUintReal",
    "hkUFloat8",
    "hkHalf16",
    "hkBaseObject",
    "hkContainerHeapAllocator",
    "hkBool",
    "hkStringPtr",
    "hkReflectType",
    "hkReflectQualifiedType",
    "hkPropertyDesc",
    "hkPtrAndInt",
    "hkReflectAny",
    "hkPropertyId",
    "hkTuple",
    "hkHashMapDetailIndex",
    "hkHashMapDetailMapTuple",
    "hkHashBase",
    "hkHashMap",
    "hkDefaultPropertyBag",
    "hkPropertyBag",
    "hkReferencedObject",
]

import typing as tp
from dataclasses import dataclass, field

import numpy as np

from soulstruct.havok.utilities.maths import Quaternion, TRSTransform, Vector3, Vector4
from soulstruct.havok.enums import TagDataType, MemberFlags
from soulstruct.havok.types.base import *

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct.havok.tagfile.structs import TagFileItem
    from soulstruct.havok.packfile.structs import PackFileDataItem


# --- Invalid Types --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkReflectDetailOpaque(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = TagDataType.Invalid

    __tag_format_flags = 9
    __real_name = "hkReflect::Detail::Opaque"
    local_members = ()


# --- Primitive Types --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _bool(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Bool | TagDataType.Int8

    __tag_format_flags = 9
    __real_name = "bool"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _int(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int32

    __tag_format_flags = 9
    __hsh = 4062341138
    __real_name = "int"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _unsigned_short(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.Int16

    __tag_format_flags = 9
    __real_name = "unsigned short"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8

    __tag_format_flags = 9
    __hsh = 4184862313
    __real_name = "char"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _charSTAR(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.CharArray

    __tag_format_flags = 9
    __real_name = "char*"
    local_members = ()

    @classmethod
    def get_data_type(cls):
        return _char


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _const_charSTAR(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.ConstCharArray

    __tag_format_flags = 9
    __real_name = "const char*"
    local_members = ()

    @classmethod
    def get_data_type(cls):
        return _char


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _float(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.FloatAndFloat32

    __tag_format_flags = 9
    __real_name = "float"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _short(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int16

    __tag_format_flags = 9
    __real_name = "short"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _signed_char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8

    __tag_format_flags = 9
    __real_name = "signed char"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _unsigned_long_long(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Int | TagDataType.Int64

    __tag_format_flags = 9
    __real_name = "unsigned long long"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _unsigned_int(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Int | TagDataType.Int32

    __tag_format_flags = 9
    __real_name = "unsigned int"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _unsigned_char(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.Int8

    __tag_format_flags = 9
    __real_name = "unsigned char"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _void(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = TagDataType.Void

    __tag_format_flags = 25
    __abstract_value = 1
    __real_name = "void"
    local_members = ()


# --- Havok Struct Types --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkVector4f(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Struct | 4 << 8

    __tag_format_flags = 11
    __hsh = 3041566998
    local_members = ()

    @classmethod
    def unpack_tagfile(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> Vector4:
        value = Vector4(super(hkVector4f, cls).unpack_tagfile(reader, offset, items))
        return value

    @classmethod
    def unpack_packfile(cls, item: PackFileDataItem, offset: int = None) -> Vector4:
        value = Vector4(super(hkVector4f, cls).unpack_packfile(item, offset))
        return value

    @classmethod
    def unpack_primitive_array(cls, reader: BinaryReader, length: int, offset: int = None) -> np.ndarray:
        """Unpack an array of vectors with `numpy`."""
        data = reader.read(length * 4 * cls.length, offset=offset)
        dtype = np.dtype(f"{reader.byte_order}f4")
        return np.frombuffer(data, dtype=dtype).reshape((length, cls.length))


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkQuaternionf(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Struct | 4 << 8

    __tag_format_flags = 43

    local_members = (
        Member(0, "vec", hkVector4f),
    )
    members = local_members

    vec: Vector4

    @classmethod
    def unpack_tagfile(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> Quaternion:
        value = Quaternion(super(hkQuaternionf, cls).unpack_tagfile(reader, offset, items))
        return value

    @classmethod
    def unpack_packfile(cls, item: PackFileDataItem, offset: int = None) -> Quaternion:
        value = Quaternion(super(hkQuaternionf, cls).unpack_packfile(item, offset))
        return value


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRotationImpl(hkStruct(_float, 12)):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Struct | 12 << 8

    __tag_format_flags = 11
    local_members = ()

    __templates = (
        TemplateType("tFT", _type=_float),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkVector4(hkVector4f):
    """Havok alias."""
    __tag_format_flags = 0
    __hsh = 3266831369
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix3Impl(hkStruct(_float, 12)):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Struct | 12 << 8

    __tag_format_flags = 11
    local_members = ()

    __templates = (
        TemplateType("tFT", _type=_float),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix4Impl(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Struct | 4096

    __tag_format_flags = 43

    local_members = (
        Member(0, "col0", hkVector4f),
        Member(16, "col1", hkVector4f),
        Member(32, "col2", hkVector4f),
        Member(48, "col3", hkVector4f),
    )
    members = local_members

    col0: Vector4
    col1: Vector4
    col2: Vector4
    col3: Vector4

    __templates = (
        TemplateType("tFT", _type=_float),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix4f(hkMatrix4Impl):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRotationf(hkRotationImpl):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix3f(hkMatrix3Impl):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix4(hkMatrix4f):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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
    translation: Vector4


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix3(hkMatrix3f):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkTransform(hkTransformf):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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

    translation: Vector4 = field(default_factory=Vector4.zero)
    rotation: Quaternion = field(default_factory=Quaternion.identity)
    scale: Vector4 = field(default_factory=Vector4.one)

    @classmethod
    def identity(cls):
        return cls(
            translation=Vector4.zero(),
            rotation=Quaternion.identity(),
            scale=Vector4.one(),
        )

    def to_trs_transform(self) -> TRSTransform:
        return TRSTransform(Vector3.from_vector4(self.translation), self.rotation, Vector3.from_vector4(self.scale))

    @classmethod
    def from_trs_transform(cls, transform: TRSTransform):
        return cls(
            translation=Vector4((*transform.translation, 1.0)),
            rotation=transform.rotation,
            scale=Vector4((*transform.scale, 1.0)),
        )


# --- Havok Wrappers --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkQsTransform(hkQsTransformf):
    """Havok alias."""
    __tag_format_flags = 0
    __hsh = 3766916239
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUint32(_unsigned_int):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkQuaternion(hkQuaternionf):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUint16(_unsigned_short):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkReal(_float):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkInt16(_short):
    """Havok alias."""
    __tag_format_flags = 0
    __hsh = 1556469994
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkInt32(_int):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkInt8(_signed_char):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUlong(_unsigned_long_long):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUint8(_unsigned_char):
    """Havok alias."""
    __tag_format_flags = 0
    __hsh = 3721671547
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUint64(_unsigned_long_long):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUintReal(_unsigned_int):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
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


@dataclass(slots=True, eq=False, repr=False)
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


# --- Havok Core Types --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkBaseObject(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 144
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkContainerHeapAllocator(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 16
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkStringPtr(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.ConstCharArray

    __tag_format_flags = 41
    __hsh = 2710609657

    local_members = (
        Member(0, "stringAndFlag", _charSTAR, MemberFlags.Private),
    )
    members = local_members

    stringAndFlag: str

    @classmethod
    def get_data_type(cls):
        return _char


# --- 'hkReferenceObject' and Dependencies --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkReflectType(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = TagDataType.Invalid

    __tag_format_flags = 9
    __real_name = "hkReflect::Type"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkReflectQualifiedType(hkBasePointer):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Pointer

    __tag_format_flags = 43
    __real_name = "hkReflect::QualifiedType"
    _data_type = hkReflectType
    local_members = (
        Member(0, "type", Ptr(hkReflectType), MemberFlags.Private),
    )
    members = local_members

    type: hkReflectType

    __templates = (
        TemplateType("tTYPE", _type=hkReflectType),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkPropertyDesc(hk):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "type", Ptr(hkReflectType)),
        Member(8, "name", _const_charSTAR),
        Member(16, "flags", hkFlags(hkUint32)),
    )
    members = local_members

    type: hkReflectType
    name: _const_charSTAR
    flags: hkUint32


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkPtrAndInt(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 1

    local_members = (
        Member(0, "ptrAndInt", Ptr(hkPropertyDesc), MemberFlags.Private),
    )
    members = local_members

    ptrAndInt: hkPropertyDesc

    __templates = (
        TemplateType("tPTYPE", _type=hkPropertyDesc),
        TemplateType("tITYPE", _type=_unsigned_int),
        TemplateValue("vMASK", value=1),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkReflectAny(hk):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Array

    __tag_format_flags = 43
    __real_name = "hkReflect::Any"

    local_members = (
        Member(0, "type", hkReflectQualifiedType, MemberFlags.Private),
        Member(8, "status", _unsigned_char, MemberFlags.Private),
        Member(16, "buf", hkGenericStruct(hkUintReal, 4), MemberFlags.Private),
    )
    members = local_members

    type: hkReflectQualifiedType
    status: int
    buf: tuple[hkUintReal]


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkPropertyId(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "desc", hkPtrAndInt, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = local_members

    desc: hkPtrAndInt = None


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkTuple(hk):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "0", hkPropertyId),
        Member(16, "1", hkReflectAny),
    )
    members = local_members

    __templates = (
        TemplateType("tT0", _type=hkPropertyId),
        TemplateType("tT1", _type=hkReflectAny),
        TemplateType("tT2", _type=_void),
        TemplateType("tT3", _type=_void),
        TemplateType("tT4", _type=_void),
        TemplateType("tT5", _type=_void),
        TemplateType("tT6", _type=_void),
        TemplateType("tT7", _type=_void),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkHashMapDetailIndex(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkHashMapDetail::Index"

    local_members = (
        Member(0, "entries", Ptr(_void)),
        Member(8, "hashMod", _int),
    )
    members = local_members

    entries: _void
    hashMod: int


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkHashMapDetailMapTuple(hkTuple):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 16
    __real_name = "hkHashMapDetail::MapTuple"
    local_members = ()

    __templates = (
        TemplateType("tKEY", _type=hkPropertyId),
        TemplateType("tVALUE", _type=hkReflectAny),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkHashBase(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "items", hkArray(hkHashMapDetailMapTuple), MemberFlags.Protected),
        Member(16, "index", hkHashMapDetailIndex, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = local_members

    items: list[hkHashMapDetailMapTuple]
    index: hkHashMapDetailIndex = None

    __templates = (
        TemplateType("tITEM", _type=hkHashMapDetailMapTuple),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkHashMap(hkHashBase):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 16
    local_members = ()

    __templates = (
        TemplateType("tKEY", _type=hkPropertyId),
        TemplateType("tVALUE", _type=hkReflectAny),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkDefaultPropertyBag(hk):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "propertyMap", hkHashMap, MemberFlags.Protected),
        Member(32, "transientPropertyMap", hkHashMap, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(64, "locked", _bool, MemberFlags.NotSerializable),
    )
    members = local_members

    propertyMap: hkHashMap
    transientPropertyMap: hkHashMap = None
    locked: bool = False


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkPropertyBag(hkBasePointer):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Array

    __tag_format_flags = 43
    _data_type = hkDefaultPropertyBag
    local_members = (
        Member(0, "bag", Ptr(hkDefaultPropertyBag), MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = local_members

    bag: hkDefaultPropertyBag | None = None


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkReferencedObject(hkBaseObject):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(8, "propertyBag", hkPropertyBag, MemberFlags.Private),
        Member(16, "memSizeAndFlags", hkUint16, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(18, "refCount", hkUint16, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkBaseObject.members + local_members

    propertyBag: hkPropertyBag
    memSizeAndFlags: int = 0
    refCount: int = 0
