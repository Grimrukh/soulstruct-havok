"""Havok 2014 types that may not be present in packfiles, generally."""
from __future__ import annotations

__all__ = [
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
    "hkUint64",
    "hkUintReal",
    "hkBaseObject",
    "hkReferencedObject",
    "hkRefVariant",
    "hkUFloat8",
    "hkContainerHeapAllocator",
    "hkStringPtr",
    "hkBool",
    "hkHalf16",
]

import typing as tp

from soulstruct.utilities.maths import Vector4
from soulstruct_havok.enums import MemberFlags
from soulstruct_havok.types.core import *

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.tagfile.structs import TagFileItem


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

    @classmethod
    def unpack(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> Vector4:
        cls.debug_print_unpack(f"Unpacking `{cls.__name__}`... (hkVector4f) <{hex(offset)}>")
        cls.increment_debug_indent()
        value = Vector4(super().unpack(reader, offset, items))
        cls.decrement_debug_indent()
        cls.debug_print_unpack(f"-> {repr(value)}")
        return value


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

    col0: Vector4
    col1: Vector4
    col2: Vector4
    col3: Vector4


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
    translation: Vector4


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
        Member(0, "translation", hkVector4f),
        Member(16, "rotation", hkQuaternionf),
        Member(32, "scale", hkVector4f),
    )
    members = local_members

    translation: Vector4
    rotation: hkQuaternionf
    scale: Vector4


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
        Member(8, "memSizeAndRefCount", hkUint32, MemberFlags.NotSerializable | MemberFlags.Private),
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
        Member(0, "ptr", Ptr(hkReferencedObject), MemberFlags.Private),
    )
    members = local_members

    ptr: hkReferencedObject


class hkUFloat8(hk):
    alignment = 2
    byte_size = 1
    tag_format_flags = 41
    tag_type_flags = 7

    local_members = (
        Member(0, "value", hkUint8),
    )
    members = local_members

    value: hkUint8


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
        Member(0, "stringAndFlag", _const_char, MemberFlags.Private),
    )
    members = local_members

    stringAndFlag: _const_char


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


class hkHalf16(hk):
    alignment = 2
    byte_size = 2
    tag_format_flags = 41
    tag_type_flags = 476677

    local_members = (
        Member(0, "value", hkInt16, MemberFlags.Private),
    )
    members = local_members

    value: hkInt16
