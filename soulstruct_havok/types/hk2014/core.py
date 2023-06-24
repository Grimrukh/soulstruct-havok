"""Havok 2014 types that may not be present in packfiles, generally."""
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

    # hk2014
    "Vector4",
    "Quaternion",
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
    "hkUint64",
    "hkUintReal",
    "hkUFloat8",
    "hkHalf16",
    "hkBaseObject",
    "hkReferencedObject",
    "hkRefVariant",
    "hkContainerHeapAllocator",
    "hkStringPtr",
    "hkBool",
]

import typing as tp
from dataclasses import dataclass

from soulstruct_havok.utilities.maths import Quaternion, TRSTransform, Vector3, Vector4
from soulstruct_havok.enums import MemberFlags
from soulstruct_havok.types.hk64 import *

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.tagfile.structs import TagFileItem
    from soulstruct_havok.packfile.structs import PackFileItem


# --- Invalid Types --- #


@dataclass(slots=True, eq=False, repr=False)
class hkReflectDetailOpaque(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 9
    tag_type_flags = 1
    __real_name = "hkReflect::Detail::Opaque"
    local_members = ()


# --- Primitive Types --- #


@dataclass(slots=True, eq=False, repr=False)
class _int(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 33284

    __hsh = 4062341138
    __real_name = "int"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _const_char(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 3
    __real_name = "const char*"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _unsigned_short(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 9
    tag_type_flags = 16388
    __real_name = "unsigned short"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _char(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196

    __hsh = 4184862313
    __real_name = "char"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _float(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 1525253
    __real_name = "float"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _short(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 9
    tag_type_flags = 16900
    __real_name = "short"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _signed_char(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8708
    __real_name = "signed char"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _unsigned_long_long(hk):
    alignment = 8
    byte_size = 8
    tag_format_flags = 9
    tag_type_flags = 65540
    __real_name = "unsigned long long"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _unsigned_int(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 9
    tag_type_flags = 32772
    __real_name = "unsigned int"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _unsigned_char(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 9
    tag_type_flags = 8196
    __real_name = "unsigned char"
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class _void(hk):
    alignment = 0
    byte_size = 0
    tag_format_flags = 25
    tag_type_flags = 0

    __abstract_value = 1
    __real_name = "void"
    local_members = ()


# --- Havok Struct Types --- #


@dataclass(slots=True, eq=False, repr=False)
class hkVector4f(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_format_flags = 11
    tag_type_flags = 1064
    local_members = ()

    @classmethod
    def unpack_tagfile(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> Vector4:
        value = Vector4(super(hkVector4f, cls).unpack_tagfile(reader, offset, items))
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItem, offset: int = None) -> Vector4:
        value = Vector4(super(hkVector4f, cls).unpack_packfile(entry, offset))
        return value


@dataclass(slots=True, eq=False, repr=False)
class hkQuaternionf(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 16
    tag_format_flags = 43
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
    def unpack_packfile(cls, entry: PackFileItem, offset: int = None) -> Quaternion:
        value = Quaternion(super(hkQuaternionf, cls).unpack_packfile(entry, offset))
        return value


@dataclass(slots=True, eq=False, repr=False)
class hkRotationImpl(hkStruct(_float, 4)):
    alignment = 16
    byte_size = 48
    tag_format_flags = 11
    tag_type_flags = 3112
    local_members = ()

    __templates = (
        TemplateType("tFT", type=_float),
    )


@dataclass(slots=True, eq=False, repr=False)
class hkVector4(hkVector4f):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkMatrix3Impl(hkStruct(_float, 12)):
    alignment = 16
    byte_size = 48
    tag_format_flags = 11
    tag_type_flags = 3112
    local_members = ()

    __templates = (
        TemplateType("tFT", type=_float),
    )


@dataclass(slots=True, eq=False, repr=False)
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

    col0: Vector4
    col1: Vector4
    col2: Vector4
    col3: Vector4


@dataclass(slots=True, eq=False, repr=False)
class hkRotationf(hkRotationImpl):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkMatrix3f(hkMatrix3Impl):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkMatrix4(hkMatrix4f):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
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
    translation: Vector4


@dataclass(slots=True, eq=False, repr=False)
class hkMatrix3(hkMatrix3f):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkTransform(hkTransformf):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkQsTransformf(hk):
    alignment = 16
    byte_size = 48
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "translation", hkVector4f),
        Member(16, "rotation", hkQuaternionf),
        Member(32, "scale", hkVector4f),
    )
    members = local_members

    translation: Vector4
    rotation: Quaternion
    scale: Vector4

    def to_trs_transform(self) -> TRSTransform:
        return TRSTransform(Vector3.from_vector4(self.translation), self.rotation, Vector3.from_vector4(self.scale))

    @classmethod
    def from_trs_transform(cls, transform: TRSTransform):
        return cls(
            translation=Vector4((*transform.translation, 1.0)),
            rotation=transform.rotation,
            scale=Vector4((*transform.scale, 1.0)),
        )


@dataclass(slots=True, eq=False, repr=False)
class hkQsTransform(hkQsTransformf):
    """Havok alias."""
    __hsh = 3766916239
    local_members = ()


# --- Havok Wrappers --- #


@dataclass(slots=True, eq=False, repr=False)
class hkUint16(_unsigned_short):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkReal(_float):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkInt16(_short):
    """Havok alias."""
    __hsh = 1556469994
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkInt32(_int):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkInt8(_signed_char):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkUlong(_unsigned_long_long):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkUint32(_unsigned_int):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkUint8(_unsigned_char):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkUint64(_unsigned_long_long):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkUintReal(_unsigned_int):
    """Havok alias."""
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkUFloat8(hk):
    alignment = 2
    byte_size = 1
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "value", hkUint8),
    )
    members = local_members

    value: int

    def __eq__(self, other: hkUFloat8):
        if not isinstance(other, hkUFloat8):
            return False
        return self.value == other.value

    def __repr__(self):
        return f"hkUFloat8({self.value})"


@dataclass(slots=True, eq=False, repr=False)
class hkHalf16(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 41
    tag_type_flags = 476677

    local_members = (
        Member(0, "value", hkInt16, MemberFlags.Private),
    )
    members = local_members

    value: int

    def __eq__(self, other: hkHalf16):
        if not isinstance(other, hkHalf16):
            return False
        return self.value == other.value

    def __repr__(self):
        return f"hkHalf16({self.value})"


# --- Havok Core Types --- #


@dataclass(slots=True, eq=False, repr=False)
class hkBaseObject(hk):
    alignment = 8
    byte_size = 8
    tag_format_flags = 41
    tag_type_flags = 7
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkReferencedObject(hkBaseObject):
    alignment = 16
    byte_size = 16
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(8, "memSizeAndRefCount", hkUint32, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkBaseObject.members + local_members

    memSizeAndRefCount: hkUint32


@dataclass(slots=True, eq=False, repr=False)
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


@dataclass(slots=True, eq=False, repr=False)
class hkContainerHeapAllocator(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 57
    tag_type_flags = 7

    __abstract_value = 16
    local_members = ()


@dataclass(slots=True, eq=False, repr=False)
class hkStringPtr(hk):
    alignment = 4
    byte_size = 4
    tag_format_flags = 41
    tag_type_flags = 3

    __hsh = 2837000324

    local_members = (
        Member(0, "stringAndFlag", _const_char, MemberFlags.Private),
    )
    members = local_members

    stringAndFlag: _const_char


@dataclass(slots=True, eq=False, repr=False)
class hkBool(hk):
    alignment = 1
    byte_size = 1
    tag_format_flags = 41
    tag_type_flags = 8194

    local_members = (
        Member(0, "bool", _char, MemberFlags.Private),
    )
    members = local_members

    bool: _char
