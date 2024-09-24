from __future__ import annotations

__all__ = [
    "PackMemberType",
    "PackMemberFlags",
    "PACK_MEMBER_TYPE_PY_TYPE_NAMES",
    "HKXTagFileType",
    "TagDataType",
    "TagFormatFlags",
    "MemberFlags",
]

from enum import IntEnum, StrEnum
from pathlib import Path

from soulstruct.utilities.binary import BinaryReader


class PyHavokModule(StrEnum):
    """Supported Havok versions in `soulstruct-havok`."""
    hk550 = "550"    # Demon's Souls
    hk2010 = "2010"  # DS1:PTDE
    hk2014 = "2014"  # Bloodborne
    hk2015 = "2015"  # DS1:Remastered
    hk2016 = "2016"  # DS3
    hk2018 = "2018"  # Elden Ring


class PackMemberType(IntEnum):
    """Indicates data type of a `packfile` type's member, as indicated in files containing HK type definitions.

    These are explicitly just references to Havok primitives that are not defined in any packfiles. The primitive
    types can be looked up from a full `HKXTypeList` by these enum names directly.

    Type is always unique - that is, these are not bit flags that can be combined.

    For `hkRefPtr`, `hkArray`, and `hkEnum` types, a second byte will indicate the type of that pointer/array or the
    size of that enum.

    See: https://code.botw.link/uking/uking/lib/hkStubs/Havok/Common/Base/Reflection/hkClassMember.h.html
    """
    TYPE_VOID = 0
    TYPE_BOOL = 1  # hkBool
    TYPE_CHAR = 2
    TYPE_INT8 = 3  # hkInt8
    TYPE_UINT8 = 4  # hkUint8
    TYPE_INT16 = 5  # hkInt16
    TYPE_UINT16 = 6  # hkUint16
    TYPE_INT32 = 7  # hkInt32
    TYPE_UINT32 = 8  # hkUint32
    TYPE_INT64 = 9  # hkInt64
    TYPE_UINT64 = 10  # hkUint64
    TYPE_REAL = 11  # hkReal  # TODO: `float` itself used by non-primitive: hkxMeshSection["linearKeyFrameHints"]
    TYPE_VECTOR4 = 12  # hkVector4
    TYPE_QUATERNION = 13  # hkQuaternionf
    TYPE_MATRIX3 = 14  # hkMatrix3
    TYPE_ROTATION = 15  # TODO: Not observed.
    TYPE_QSTRANSFORM = 16  # hkQsTransform (translation, rotation, scale)
    TYPE_MATRIX4 = 17  # hkMatrix4
    TYPE_TRANSFORM = 18  # hkTransform (rotation, translation)
    TYPE_ZERO = 19  # TODO: Not observed.
    TYPE_POINTER = 20  # Ptr (single object, either Class or Void)
    TYPE_FUNCTIONPOINTER = 21  # TODO: Not observed.
    TYPE_ARRAY = 22  # hkArray[T], T in second byte
    TYPE_INPLACEARRAY = 23  # hkInplaceArray[T, N]  # TODO: Not observed.
    TYPE_ENUM = 24  # hkEnum[ENUM, STORAGE], always has a `hkClassEnum` entry pointer, enum size in second byte
    TYPE_STRUCT = 25  # hkClass, always has a `hkClass` entry pointer, no subtype
    TYPE_SIMPLEARRAY = 26  # TODO: Not observed.
    TYPE_HOMOGENOUSARRAY = 27  # TODO: Not observed.
    TYPE_VARIANT = 28  # TODO: Not observed?
    TYPE_CSTRING = 29  # TODO: Not observed.
    TYPE_ULONG = 30  # hkUlong, distinct from `hkUInt64` and "guaranteed to be the same size as a pointer" (rare)
    TYPE_FLAGS = 31  # hkFlags[SOTRAGE]  # TODO: storage size in second byte?
    TYPE_HALF = 32  # hkHalf16
    TYPE_STRINGPTR = 33  # hkStringPtr
    TYPE_RELARRAY = 34  # hkRelArray, stores packed array data at a relative offset
    TYPE_MAX = 35  # TODO: Not observed.

    def get_py_type_name(self):
        try:
            return PACK_MEMBER_TYPE_PY_TYPE_NAMES[self]
        except KeyError:
            raise KeyError(f"Python type name for packfile member type {self.name} is unknown.")

    def get_true_py_type_name(self):
        try:
            return PACK_MEMBER_TYPE_PY_TYPES[self]
        except KeyError:
            try:
                return self.get_py_type_name()
            except KeyError:
                raise KeyError(f"Python true type name for packfile member type {self.name} is unknown.")

    @classmethod
    def is_builtin_type(cls, py_type_name: str):
        return py_type_name.split("[")[0] in {"hkStruct"} | set(PACK_MEMBER_TYPE_PY_TYPE_NAMES.values())


PACK_MEMBER_TYPE_PY_TYPE_NAMES = {
    PackMemberType.TYPE_VOID: "_void",
    PackMemberType.TYPE_BOOL: "hkBool",
    PackMemberType.TYPE_CHAR: "hkChar",
    PackMemberType.TYPE_INT8: "hkInt8",
    PackMemberType.TYPE_UINT8: "hkUint8",
    PackMemberType.TYPE_INT16: "hkInt16",
    PackMemberType.TYPE_UINT16: "hkUint16",
    PackMemberType.TYPE_INT32: "hkInt32",
    PackMemberType.TYPE_UINT32: "hkUint32",
    PackMemberType.TYPE_INT64: "hkInt64",
    PackMemberType.TYPE_UINT64: "hkUint64",
    PackMemberType.TYPE_REAL: "hkReal",
    PackMemberType.TYPE_VECTOR4: "hkVector4",
    PackMemberType.TYPE_QUATERNION: "hkQuaternionf",
    PackMemberType.TYPE_MATRIX3: "hkMatrix3",
    # PackMemberType.TYPE_ROTATION: "",
    PackMemberType.TYPE_QSTRANSFORM: "hkQsTransform",
    PackMemberType.TYPE_MATRIX4: "hkMatrix4",
    PackMemberType.TYPE_TRANSFORM: "hkTransform",
    # PackMemberType.TYPE_ZERO: "",
    PackMemberType.TYPE_POINTER: "Ptr",
    # PackMemberType.TYPE_FUNCTIONPOINTER: "",
    PackMemberType.TYPE_ARRAY: "hkArray",
    # PackMemberType.TYPE_INPLACEARRAY: "",
    PackMemberType.TYPE_ENUM: "hkEnum",
    # PackMemberType.TYPE_STRUCT: "hkClass",
    # PackMemberType.TYPE_SIMPLEARRAY: "",
    # PackMemberType.TYPE_HOMOGENOUSARRAY: "",
    # PackMemberType.TYPE_VARIANT: "",
    # PackMemberType.TYPE_CSTRING: "",
    PackMemberType.TYPE_ULONG: "hkUlong",
    PackMemberType.TYPE_FLAGS: "hkFlags",
    PackMemberType.TYPE_HALF: "hkHalf16",
    PackMemberType.TYPE_STRINGPTR: "hkStringPtr",
    PackMemberType.TYPE_RELARRAY: "hkRelArray",
    # PackMemberType.TYPE_MAX: "",
}

PACK_MEMBER_TYPE_PY_TYPES = {
    # PackMemberType.TYPE_VOID: "_void",
    PackMemberType.TYPE_BOOL: "bool",
    PackMemberType.TYPE_CHAR: "int",
    PackMemberType.TYPE_INT8: "int",
    PackMemberType.TYPE_UINT8: "int",
    PackMemberType.TYPE_INT16: "int",
    PackMemberType.TYPE_UINT16: "int",
    PackMemberType.TYPE_INT32: "int",
    PackMemberType.TYPE_UINT32: "int",
    PackMemberType.TYPE_INT64: "int",
    PackMemberType.TYPE_UINT64: "int",
    PackMemberType.TYPE_REAL: "float",
    # PackMemberType.TYPE_VECTOR4: "hkVector4",
    # PackMemberType.TYPE_QUATERNION: "hkQuaternionf",
    # PackMemberType.TYPE_MATRIX3: "hkMatrix3",
    # PackMemberType.TYPE_ROTATION: "",
    # PackMemberType.TYPE_QSTRANSFORM: "hkQsTransform",
    # PackMemberType.TYPE_MATRIX4: "hkMatrix4",
    # PackMemberType.TYPE_TRANSFORM: "hkTransform",
    # PackMemberType.TYPE_ZERO: "",
    # PackMemberType.TYPE_POINTER: "Ptr",
    # PackMemberType.TYPE_FUNCTIONPOINTER: "",
    PackMemberType.TYPE_ARRAY: "list",
    # PackMemberType.TYPE_INPLACEARRAY: "",
    # PackMemberType.TYPE_ENUM: "hkEnum",
    # PackMemberType.TYPE_STRUCT: "hkClass",
    # PackMemberType.TYPE_SIMPLEARRAY: "",
    # PackMemberType.TYPE_HOMOGENOUSARRAY: "",
    # PackMemberType.TYPE_VARIANT: "",
    # PackMemberType.TYPE_CSTRING: "",
    PackMemberType.TYPE_ULONG: "int",
    # PackMemberType.TYPE_FLAGS: "hkFlags",
    PackMemberType.TYPE_HALF: "hkHalf16",
    PackMemberType.TYPE_STRINGPTR: "str",
    PackMemberType.TYPE_RELARRAY: "list",
    # PackMemberType.TYPE_MAX: "",
}


class PackMemberFlags(IntEnum):
    """Flags for members in packfiles.

    See: https://code.botw.link/uking/uking/lib/hkStubs/Havok/Common/Base/Reflection/hkClassMember.h.html
    """
    FLAGS_NONE = 0
    ALIGN_8 = 1 << 7
    ALIGN_16 = 1 << 8
    NOT_OWNED = 1 << 9
    SERIALIZED_IGNORED = 1 << 10
    ALIGN_32 = 1 << 11
    # TODO: ALIGN_REAL = ALIGN_32 if HK_REAL_IS_DOUBLE else ALIGN_16


class HKXTagFileType(IntEnum):
    Invalid = -1
    Object = 0
    Compendium = 1

    @classmethod
    def from_file(cls, hkx_file_path: Path) -> HKXTagFileType:
        """Detect tagfile type by peeking inside file."""
        reader = BinaryReader(hkx_file_path)
        magic = reader.unpack("4s", offset=4)
        if magic == b"TAG0":
            return cls.Object
        elif magic == b"TCM0":
            return cls.Compendium
        else:
            return cls.Invalid


class TagDataType(IntEnum):
    """Data type of a given HKX type, as used in tagfiles. Different to packfile enumeration.

    The lowest byte indicates the data type. For integers, the second-lowest byte, and one bit of the third-lowest byte
    (for `Int64`), are used to indicate the sign and size of the integer type.

    The exception is `Float32`, which has a unique signature spanning the two lowest bytes.

    Note that the lowest byte values are UNIQUE. `Pointer`, `Class`, `Array`, and `Tuple` types indicate the data type
    of the thing they point to or store using the `HKXType.pointer` attribute.
    """

    # LOWEST BYTE

    Void = 0b00000000  # 0
    Invalid = 0b00000001  # 1
    Bool = 0b00000010  # 2
    CharArray = 0b00000011  # 3  # `char*`; also type of `const char*` and `hkStringPtr` in older Havok
    Int = 0b00000100  # 4
    Float = 0b00000101  # 5
    Pointer = 0b00000110  # 6
    Class = 0b00000111  # 7
    Array = 0b00001000  # 8  # also type of `hkPropertyBag` and `hkReflect::Type` in newer Havok
    Struct = 0b00101000  # 40
    ConstCharArray = 0b10000011  # 131  # type of `const char*` and `hkStringPtr` in newer Havok

    # HIGHER BYTES

    # NOTE: `Struct` subtypes use the second byte to indicate their length. I assume this means their maximum length is
    # 255, though they may also just continue to use higher bits.

    # `Int` subtypes
    IsSigned = 0b0_00000010 << 8  # combined with one of the four types below
    Int8 = 0b0_00100000 << 8
    Int16 = 0b0_01000000 << 8
    Int32 = 0b0_10000000 << 8
    Int64 = 0b1_00000000 << 8

    # `Float` subtypes
    # There is a `hkUFloat8` class as well, but its type flags are actually marked as `Class` here (has "value" member).
    Float16 = 0b00000111_01000110 << 8  # has a `hkInt16` member called "value"
    Float32 = 0b00010111_01000110 << 8

    FloatAndFloat32 = Float | Float32

    def has_flag(self, tagfile_types: int):
        return bool(tagfile_types & self.value)

    @classmethod
    def from_packfile_integer(cls, packfile_type: PackMemberType) -> int:
        """Construct flags from given `PackMemberType`.

        Raises a `TypeError` if called on non-integer type.
        """
        if packfile_type == PackMemberType.TYPE_UINT8:
            return cls.Int | cls.Int8
        elif packfile_type == PackMemberType.TYPE_INT8:
            return cls.Int | cls.Int8 | cls.IsSigned
        elif packfile_type == PackMemberType.TYPE_UINT16:
            return cls.Int | cls.Int16
        elif packfile_type == PackMemberType.TYPE_INT16:
            return cls.Int | cls.Int16 | cls.IsSigned
        elif packfile_type == PackMemberType.TYPE_UINT32:
            return cls.Int | cls.Int32
        elif packfile_type == PackMemberType.TYPE_INT32:
            return cls.Int | cls.Int32 | cls.IsSigned
        elif packfile_type == PackMemberType.TYPE_UINT64:
            return cls.Int | cls.Int64
        elif packfile_type == PackMemberType.TYPE_INT64:
            return cls.Int | cls.Int64 | cls.IsSigned
        else:
            raise TypeError(f"Given `PackMemberType` is not an integer type: {packfile_type.name}")

    @classmethod
    def get_int_fmt(cls, tagfile_types: int, signed=False, count=1):
        """Get struct format based on integer size, sign, and count (for "simple" arrays/tuples).

        Raises a `TypeError` if called on non-integer type.
        """
        if tagfile_types & cls.Int8:
            fmt = f"{count}B"
        elif tagfile_types & cls.Int16:
            fmt = f"{count}H"
        elif tagfile_types & cls.Int32:
            fmt = f"{count}I"
        elif tagfile_types & cls.Int64:
            fmt = f"{count}Q"
        else:
            raise TypeError(f"Cannot get struct format for node sub-type flags {tagfile_types}.")
        return fmt.lower() if tagfile_types & cls.IsSigned or signed else fmt

    def get_primitive_type_hint(self) -> str:
        if self == self.Bool:
            return "bool"
        if self == self.CharArray:
            return "str"
        if self == self.Int:
            return "int"
        if self == self.Float:
            return "float"
        return ""


class TagFormatFlags(IntEnum):
    """Flags indicating which types of data are stored in a tagfile `TypeInfo` as variable ints."""

    SubType = 0b0000_0001  # everything except Void (hk primitives)
    Pointer = 0b0000_0010  # pointers, arrays, and tuples (versus everything else)
    Version = 0b0000_0100  # most higher-level classes
    ByteSize = 0b0000_1000  # everything except Void (hk primitives)
    AbstractValue = 0b0001_0000  # some classes and the unique `void` type
    Members = 0b0010_0000  # all classes, arrays, pointers (except `T*`), and the unique `hkBool` type (wraps `char`)
    Interfaces = 0b0100_0000  # very rare (`hkpShapeContainer` is an interface type of just two other types)
    Unknown = 0b1000_0000  # not observed

    @classmethod
    def get_packfile_type_flags(cls, has_version: bool, has_abstract_value=False) -> int:
        """Return the tag format flags for a type defined in a packfile "type" section.

        The only flags that really vary here are `Version` and `AbstractValue`.
        """
        flags = cls.SubType | cls.ByteSize | cls.Members  # 41
        if has_version:
            flags |= cls.Version
        if has_abstract_value:
            flags |= cls.AbstractValue
        return flags

    @classmethod
    def get_pointer_flags(cls, has_members: bool) -> int:
        """Return the tag format flags for an array/pointer type defined in a packfile "type" section."""
        flags = cls.SubType | cls.Pointer | cls.ByteSize  # 11
        if has_members:
            flags |= cls.Members  # 43
        return flags


class MemberFlags(IntEnum):
    """Flags indicating properties of a member.

    These are TAGFILE flags. Old packfiles use a different member flag enum, `PackMemberFlags`, whose options do not
    overlap perfectly with this newer class.
    """

    NotSerializable = 0b0000_0001  # 1  # '+nosave' or '+serialized(false)' comments in Havok headers?
    Protected = 0b0000_0010  # 2  # protected member in Havok class
    Private = 0b0000_0100  # 4  # private member in Havok class
    Default = 0b0010_0000  # 32 (always enabled)

    @classmethod
    def from_packfile_member_flags(cls, packfile_member_flags: int):
        flags = cls.Default
        if packfile_member_flags & PackMemberFlags.SERIALIZED_IGNORED:
            flags |= cls.NotSerializable
        # TODO: Not sure if `Protected` and `Private` have any analogous options in `PackMemberFlags`.
        return flags
