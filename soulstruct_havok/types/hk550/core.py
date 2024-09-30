"""Havok 2010 core types."""
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

    # 32-bit factory functions
    "Ptr",
    "hkRefPtr",
    "hkRefVariant",
    "hkArray",
    "hkViewPtr",
    "hkRelArray",
    "hkEnum",
    "hkStruct",
    "hkGenericStruct",
    "hkFreeListArrayElement",
    "hkFreeListArray",
    "hkFlags",

    # hk2010
    "Vector4",
    "hkReflectDetailOpaque",
    "_int",
    "_const_char",
    "_unsigned_short",
    "_char",
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
    "hkMatrix4",
    "hkTransformf",
    "hkMatrix3",
    "hkTransform",
    "hkQsTransformf",
    "hkQsTransform",
    "hkUint16",
    "hkReal",
    "hkInt16",
    "hkInt32",
    "hkInt8",
    "hkUlong",
    "hkUint32",
    "hkUint8",
    "hkQuaternion",
    "hkUint64",
    "hkUintReal",
    "hkHalf16",
    "hkBaseObject",
    "hkReferencedObject",
    "hkRefVariant",
    "hkContainerHeapAllocator",
    "hkStringPtr",
    "hkBool",
]

import typing as tp
from dataclasses import dataclass, field

import numpy as np

from soulstruct_havok.utilities.maths import Quaternion, TRSTransform, Vector3, Vector4
from soulstruct_havok.enums import MemberFlags
from soulstruct_havok.types.base import *

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.tagfile.structs import TagFileItem
    from soulstruct_havok.packfile.structs import PackFileDataItem


# --- Invalid Types --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkReflectDetailOpaque(hk):
    alignment = 0
    byte_size = 0
    __tag_format_flags = 9
    tag_type_flags = 1
    __real_name = "hkReflect::Detail::Opaque"
    local_members = ()


# --- Primitive Types --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _int(hk):
    alignment = 4
    byte_size = 4
    __tag_format_flags = 9
    tag_type_flags = 33284

    __hsh = 4062341138
    __real_name = "int"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _const_char(hk):
    alignment = 4
    byte_size = 4
    __tag_format_flags = 9
    tag_type_flags = 3
    __real_name = "const char*"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _unsigned_short(hk):
    alignment = 2
    byte_size = 2
    __tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "unsigned short"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _char(hk):
    alignment = 1
    byte_size = 1
    __tag_format_flags = 9
    tag_type_flags = 8196

    __hsh = 4184862313
    __real_name = "char"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _float(hk):
    alignment = 4
    byte_size = 4
    __tag_format_flags = 9
    tag_type_flags = 1525253
    __real_name = "float"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _short(hk):
    alignment = 2
    byte_size = 2
    __tag_format_flags = 9
    tag_type_flags = 16900
    __real_name = "short"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _signed_char(hk):
    alignment = 1
    byte_size = 1
    __tag_format_flags = 9
    tag_type_flags = 8708
    __real_name = "signed char"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _unsigned_long_long(hk):
    alignment = 8
    byte_size = 8
    __tag_format_flags = 9
    tag_type_flags = 65540
    __real_name = "unsigned long long"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _unsigned_int(hk):
    alignment = 4
    byte_size = 4
    __tag_format_flags = 9
    tag_type_flags = 32772
    __real_name = "unsigned int"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _unsigned_char(hk):
    alignment = 1
    byte_size = 1
    __tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "unsigned char"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _void(hk):
    alignment = 0
    byte_size = 0
    __tag_format_flags = 25
    tag_type_flags = 0

    __abstract_value = 1
    __real_name = "void"
    local_members = ()


# --- Havok Struct Types --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkVector4f(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    __tag_format_flags = 11
    tag_type_flags = 1064
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
        dtype = np.dtype(f"{reader.default_byte_order}f4")
        return np.frombuffer(data, dtype=dtype).reshape((length, cls.length))


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkQuaternionf(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    __tag_format_flags = 43
    tag_type_flags = 1064

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
    __tag_format_flags = 11
    tag_type_flags = 3112
    local_members = ()

    __templates = (
        TemplateType("tFT", _type=_float),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkVector4(hkVector4f):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix3Impl(hkStruct(_float, 12)):
    alignment = 16
    byte_size = 48
    __tag_format_flags = 11
    tag_type_flags = 3112
    local_members = ()

    __templates = (
        TemplateType("tFT", _type=_float),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix4f(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    __tag_format_flags = 43
    tag_type_flags = 4136

    local_members = (
        Member(0, "col0", hkVector4f, MemberFlags.Protected),
        Member(16, "col1", hkVector4f, MemberFlags.Protected),
        Member(32, "col2", hkVector4f, MemberFlags.Protected),
        Member(48, "col3", hkVector4f, MemberFlags.Protected),
    )
    members = local_members

    col0: Vector4
    col1: Vector4
    col2: Vector4
    col3: Vector4


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRotationf(hkRotationImpl):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix3f(hkMatrix3Impl):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkMatrix4(hkMatrix4f):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkTransformf(hkStruct(_float, 16)):
    alignment = 16
    byte_size = 64
    __tag_format_flags = 43
    tag_type_flags = 4136

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
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkTransform(hkTransformf):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkQsTransformf(hk):
    alignment = 16
    byte_size = 48
    __tag_format_flags = 41
    tag_type_flags = 7

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


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkQsTransform(hkQsTransformf):
    """Havok alias."""
    __hsh = 3766916239
    local_members = ()


# --- Havok Wrappers --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUint16(_unsigned_short):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkReal(_float):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkInt16(_short):
    """Havok alias."""
    __hsh = 1556469994
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkInt32(_int):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkInt8(_signed_char):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUlong(_unsigned_int):
    """Havok alias. TODO: 32-bit in DeS (matches pointer size). Hard-coding that in parent class here."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUint32(_unsigned_int):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUint8(_unsigned_char):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkQuaternion(hkQuaternionf):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUint64(_unsigned_long_long):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkUintReal(_unsigned_int):
    """Havok alias."""
    local_members = ()


# NOTE: No `hkUFloat8` in 550.


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkHalf16(hk):
    alignment = 2
    byte_size = 2
    __tag_format_flags = 41
    tag_type_flags = 476677

    local_members = (
        Member(0, "value", hkInt16, MemberFlags.Private),
    )
    members = local_members

    value: int


# --- Havok Core Types --- #


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkBaseObject(hk):
    alignment = 4
    byte_size = 4
    __tag_format_flags = 41
    tag_type_flags = 7
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkReferencedObject(hkBaseObject):
    alignment = 8
    byte_size = 8
    __tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(4, "memSizeAndFlags", hkUint16, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(6, "referenceCount", hkUint16, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkBaseObject.members + local_members

    memSizeAndFlags: int = 0
    referenceCount: int = 0


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRefVariant(hk):
    alignment = 8
    byte_size = 8
    __tag_format_flags = 43
    tag_type_flags = 6

    __hsh = 2872857893

    local_members = (
        Member(0, "ptr", Ptr(hkReferencedObject), MemberFlags.Private),
    )
    members = local_members

    ptr: hkReferencedObject


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkContainerHeapAllocator(hk):
    alignment = 1
    byte_size = 1
    __tag_format_flags = 57
    tag_type_flags = 7

    __abstract_value = 16
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkStringPtr(hk):
    alignment = 4
    byte_size = 4
    __tag_format_flags = 41
    tag_type_flags = 3

    __hsh = 2837000324

    local_members = (
        Member(0, "stringAndFlag", _const_char, MemberFlags.Private),
    )
    members = local_members

    stringAndFlag: _const_char


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkBool(hk):
    alignment = 1
    byte_size = 1
    __tag_format_flags = 41
    tag_type_flags = 8194

    local_members = (
        Member(0, "bool", _char, MemberFlags.Private),
    )
    members = local_members

    bool: _char
