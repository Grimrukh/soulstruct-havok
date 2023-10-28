"""Havok 2015 core types."""
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

    # hk2015
    "Vector4",
    "hkReflectDetailOpaque",
    "_bool",
    "_int",
    "_const_charSTAR",
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
    "hkBaseObject",
    "hkContainerHeapAllocator",
    "hkBool",
    "hkStringPtr",
    "hkReferencedObject",
]

import typing as tp
from dataclasses import dataclass

import numpy as np

from soulstruct_havok.utilities.maths import Quaternion, TRSTransform, Vector3, Vector4
from soulstruct_havok.enums import TagDataType, MemberFlags
from soulstruct_havok.types.hk64 import *

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.tagfile.structs import TagFileItem
    from soulstruct_havok.packfile.structs import PackFileItem


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
    __real_name = "int"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class _const_charSTAR(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.CharArray

    __tag_format_flags = 9
    __real_name = "const char*"
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
class _float(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Float | TagDataType.Float32

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
    local_members = ()

    @classmethod
    def unpack_tagfile(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> Vector4:
        value = Vector4(super(hkVector4f, cls).unpack_tagfile(reader, offset, items))
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItem, offset: int = None) -> Vector4:
        value = Vector4(super(hkVector4f, cls).unpack_packfile(entry, offset))
        return value

    @classmethod
    def try_unpack_array_tagfile(cls, reader: BinaryReader, item: TagFileItem) -> bool:
        """Unpack vector array with `numpy`."""
        data = reader.read(item.length * 4 * cls.length, offset=item.absolute_offset)
        item.value = np.frombuffer(data, dtype=np.float32).reshape((item.length, cls.length))
        return True

    @classmethod
    def try_pack_array_tagfile(
        cls, item: TagFileItem, value: list | np.ndarray
    ) -> bool:
        """Pack `float32` array in standard row-first order."""
        if not isinstance(value, np.ndarray) or value.dtype != np.float32:
            raise ValueError(f"Cannot pack non-`np.float32` array as an array of `{cls.__name__}`.")
        if value.shape[1] != cls.length:
            raise ValueError(f"Cannot pack `{cls.__name__}` array with shape {value.shape}.")
        item.writer.append(value.tobytes())
        return True


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
    def unpack_packfile(cls, entry: PackFileItem, offset: int = None) -> Quaternion:
        value = Quaternion(super(hkQuaternionf, cls).unpack_packfile(entry, offset))
        return value


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkRotationImpl(hkStruct(_float, 12)):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Struct | 12 << 8

    __tag_format_flags = 11
    local_members = ()

    __templates = (
        TemplateType("tFT", type=_float),
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
        TemplateType("tFT", type=_float),
    )


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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

    col0: Vector4
    col1: Vector4
    col2: Vector4
    col3: Vector4


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
    __tag_format_flags = 41
    tag_type_flags = TagDataType.Class

    local_members = (
        Member(0, "translation", hkVector4f),
        Member(16, "rotation", hkQuaternionf),
        Member(32, "scale", hkVector4f),
    )
    members = local_members

    translation: Vector4
    rotation: Quaternion
    scale: Vector4

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
    __hsh = 4179182467
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
    tag_type_flags = TagDataType.CharArray

    __tag_format_flags = 41
    __hsh = 2837000324

    local_members = (
        Member(0, "stringAndFlag", _const_charSTAR, MemberFlags.Private),
    )
    members = local_members

    stringAndFlag: str


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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

    memSizeAndFlags: int = 0
    refCount: int = 0
