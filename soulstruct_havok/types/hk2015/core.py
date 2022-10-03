from __future__ import annotations

__all__ = [
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

from soulstruct.utilities.maths import Quaternion, QuatTransform, Vector4
from soulstruct_havok.enums import TagDataType, MemberFlags
from soulstruct_havok.types.core import *

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.tagfile.structs import TagFileItem


# --- Invalid Types --- #


class hkReflectDetailOpaque(hk):
    alignment = 0
    byte_size = 0
    tag_type_flags = TagDataType.Invalid

    __tag_format_flags = 9
    __real_name = "hkReflect::Detail::Opaque"
    local_members = ()


# --- Primitive Types --- #


class _bool(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Bool | TagDataType.Int8

    __tag_format_flags = 9
    __real_name = "bool"
    local_members = ()


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
    tag_type_flags = TagDataType.Struct | 4 << 8

    __tag_format_flags = 43

    local_members = (
        Member(0, "vec", hkVector4f),
    )
    members = local_members

    vec: Vector4

    @classmethod
    def unpack(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> Vector4:
        cls.debug_print_unpack(f"Unpacking `{cls.__name__}`... (hkQuaternionf) <{hex(offset)}>")
        cls.increment_debug_indent()
        value = Quaternion(super().unpack(reader, offset, items))
        cls.decrement_debug_indent()
        cls.debug_print_unpack(f"-> {repr(value)}")
        return value


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

    col0: Vector4
    col1: Vector4
    col2: Vector4
    col3: Vector4


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
    translation: Vector4


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

    translation: Vector4
    rotation: Quaternion
    scale: Vector4

    def to_quat_transform(self) -> QuatTransform:
        return QuatTransform(self.translation, self.rotation, self.scale)

    @classmethod
    def from_quat_transform(cls, transform: QuatTransform):
        return cls(
            translation=Vector4(*transform.translate, 1.0),
            rotation=transform.rotation,
            scale=Vector4(*transform.scale, 1.0),
        )


# --- Havok Wrappers --- #


class hkQsTransform(hkQsTransformf):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkUint32(_unsigned_int):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkQuaternion(hkQuaternionf):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkUint16(_unsigned_short):
    """Havok alias."""
    __tag_format_flags = 0
    __hsh = 4179182467
    local_members = ()


class hkReal(_float):
    """Havok alias."""
    __tag_format_flags = 0
    local_members = ()


class hkInt16(_short):
    """Havok alias."""
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
