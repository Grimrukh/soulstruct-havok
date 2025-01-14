from __future__ import annotations

__all__ = [
    "ClassMemberType",
    "PackMemberFlags",
    "PACK_MEMBER_TYPE_PY_TYPE_NAMES",
    "HKXTagFileType",
    "TagDataType",
    "TagFormatFlags",
    "MemberFlags",
]

import importlib
import typing as tp
from enum import IntEnum
from pathlib import Path
from types import ModuleType

from soulstruct.utilities.binary import BinaryReader
from .exceptions import TypeNotDefinedError

if tp.TYPE_CHECKING:
    from soulstruct_havok.types.hk import hk
    HK_T = tp.TypeVar("HK_T", bound=hk)
    TYPE_VAR_T = tp.TypeVar("TYPE_VAR_T", bound=tp.TypeVar)


class HavokModule(IntEnum):
    """Supported Havok versions in `soulstruct-havok`, with a method for dynamic submodule retrieval.

    Numeric values are used to indicate the order in which the games were released, which is useful for defining points
    when types/members were added/removed.
    """
    hk550 = 550    # Demon's Souls
    hk2010 = 2010  # Dark Souls (PTDE)
    hk2014 = 2014  # Bloodborne / DS3
    hk2015 = 2015  # Dark Souls (Remastered)
    hk2016 = 2016  # Sekiro
    hk2018 = 2018  # Elden Ring

    def get_submodule(self) -> ModuleType:
        return importlib.import_module(f"soulstruct_havok.types.{self.name}")

    def get_version_string(self) -> str:
        return self.get_submodule().VERSION

    def get_type(self, type_name: str) -> type[hk]:
        havok_type = getattr(self.get_submodule(), type_name, None)
        if havok_type is None:
            raise TypeNotDefinedError(f"Type {type_name} is not defined in Havok module {self.name}.")
        return havok_type

    def get_type_from_var(self, type_var: TYPE_VAR_T) -> type[TYPE_VAR_T]:
        # noinspection PyArgumentList
        return self.get_type_from_constraints(*type_var.__constraints__)

    def get_type_from_constraints(self, *constraints: type[HK_T]) -> type[HK_T]:
        for constraint in constraints:
            havok_type = getattr(self.get_submodule(), constraint.__name__, None)
            if havok_type is not None:
                return havok_type
        constraint_names = ", ".join(sorted({constraint.__name__ for constraint in constraints}))
        raise TypeNotDefinedError(
            f"No types in ({constraint_names}) are defined in Havok module {self.name}."
        )

    def get_all_type_names(self) -> tp.List[str]:
        return [name for name in dir(self.get_submodule()) if not name.startswith("_") and name]


class ClassMemberType(IntEnum):
    """Indicates data type of a `hk` member, as indicated in files (packfiles only) containing HK type definitions.

    These are NOT bit flags. Every member uses exactly one of these types.

    For certain types like pointers/arrays/enums, a second byte in the packfile will indicate the data type of that
    pointer/array/enum.
    """
    TYPE_VOID = 0
    TYPE_BOOL = 1  # hkBool
    TYPE_CHAR = 2  # hkChar (not implemented)
    TYPE_INT8 = 3  # hkInt8
    TYPE_UINT8 = 4  # hkUint8
    TYPE_INT16 = 5  # hkInt16
    TYPE_UINT16 = 6  # hkUint16
    TYPE_INT32 = 7  # hkInt32
    TYPE_UINT32 = 8  # hkUint32
    TYPE_INT64 = 9  # hkInt64
    TYPE_UINT64 = 10  # hkUint64
    TYPE_REAL = 11  # hkReal
    TYPE_VECTOR4 = 12  # hkVector4
    TYPE_QUATERNION = 13  # hkQuaternion
    TYPE_MATRIX3 = 14  # hkMatrix3
    TYPE_ROTATION = 15  # hkRotation (flat row-first 3x3 rotation matrix)
    TYPE_QSTRANSFORM = 16  # hkQsTransform (translation hkVector4, rotation hkQuaternion, scale hkVector4)
    TYPE_MATRIX4 = 17  # hkMatrix4
    TYPE_TRANSFORM = 18  # hkTransform (rotation hkRotation, translation hkVector4)
    TYPE_ZERO = 19  # serialize as zero (deprecated)
    TYPE_POINTER = 20  # Ptr[T] (single object, T in second byte, either Class or Void)
    TYPE_FUNCTIONPOINTER = 21  # Function pointer (not observed)
    TYPE_ARRAY = 22  # hkArray[T], T in second byte
    TYPE_INPLACEARRAY = 23  # hkInplaceArray[T, N]  # TODO: Not observed.
    TYPE_ENUM = 24  # hkEnum[ENUM, STORAGE], always has a `hkClassEnum` entry pointer, enum size in second byte
    TYPE_STRUCT = 25  # hkClass, always has a `hkClass` entry pointer, no subtype
    TYPE_SIMPLEARRAY = 26  # [void* ptr, int size] pair (simple array of homogenous types)
    TYPE_HOMOGENOUSARRAY = 27  # TODO: hk550 only. Treating like TYPE_SIMPLEARRAY for now.
    TYPE_VARIANT = 28  # TODO: hk550 only. Treating like TYPE_POINTER for now.
    TYPE_CSTRING = 29  # TODO: hk550 only. Treating like TYPE_STRINGPTR for now.
    TYPE_ULONG = 30  # hkUlong, distinct from `hkUInt64` and "guaranteed to be the same size as a pointer" (rare)
    TYPE_FLAGS = 31  # hkFlags[SOTRAGE]  # TODO: storage size in second byte?
    TYPE_HALF = 32  # hkHalf16
    TYPE_STRINGPTR = 33  # hkStringPtr
    TYPE_RELARRAY = 34  # hkRelArray, stores packed array data at a relative offset ("attached const array values")
    TYPE_MAX = 35  # TODO: Not observed, maybe designed as enum terminator.

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
    ClassMemberType.TYPE_VOID: "_void",
    ClassMemberType.TYPE_BOOL: "hkBool",
    ClassMemberType.TYPE_CHAR: "hkChar",
    ClassMemberType.TYPE_INT8: "hkInt8",
    ClassMemberType.TYPE_UINT8: "hkUint8",
    ClassMemberType.TYPE_INT16: "hkInt16",
    ClassMemberType.TYPE_UINT16: "hkUint16",
    ClassMemberType.TYPE_INT32: "hkInt32",
    ClassMemberType.TYPE_UINT32: "hkUint32",
    ClassMemberType.TYPE_INT64: "hkInt64",
    ClassMemberType.TYPE_UINT64: "hkUint64",
    ClassMemberType.TYPE_REAL: "hkReal",
    ClassMemberType.TYPE_VECTOR4: "hkVector4",
    ClassMemberType.TYPE_QUATERNION: "hkQuaternionf",
    ClassMemberType.TYPE_MATRIX3: "hkMatrix3",
    ClassMemberType.TYPE_ROTATION: "hkRotation",
    ClassMemberType.TYPE_QSTRANSFORM: "hkQsTransform",
    ClassMemberType.TYPE_MATRIX4: "hkMatrix4",
    ClassMemberType.TYPE_TRANSFORM: "hkTransform",
    # ClassMemberType.TYPE_ZERO: "",
    ClassMemberType.TYPE_POINTER: "Ptr",
    # ClassMemberType.TYPE_FUNCTIONPOINTER: "",
    ClassMemberType.TYPE_ARRAY: "hkArray",
    # ClassMemberType.TYPE_INPLACEARRAY: "",
    ClassMemberType.TYPE_ENUM: "hkEnum",
    # ClassMemberType.TYPE_STRUCT: "hkClass",
    ClassMemberType.TYPE_SIMPLEARRAY: "SimpleArray",
    ClassMemberType.TYPE_HOMOGENOUSARRAY: "SimpleArray",
    ClassMemberType.TYPE_VARIANT: "Ptr",  # TODO: trying
    ClassMemberType.TYPE_CSTRING: "hkStringPtr",  # TODO: trying
    ClassMemberType.TYPE_ULONG: "hkUlong",
    ClassMemberType.TYPE_FLAGS: "hkFlags",
    ClassMemberType.TYPE_HALF: "hkHalf16",
    ClassMemberType.TYPE_STRINGPTR: "hkStringPtr",
    ClassMemberType.TYPE_RELARRAY: "hkRelArray",
    # ClassMemberType.TYPE_MAX: "",
}

PACK_MEMBER_TYPE_PY_TYPES = {
    # ClassMemberType.TYPE_VOID: "_void",
    ClassMemberType.TYPE_BOOL: "bool",
    ClassMemberType.TYPE_CHAR: "int",
    ClassMemberType.TYPE_INT8: "int",
    ClassMemberType.TYPE_UINT8: "int",
    ClassMemberType.TYPE_INT16: "int",
    ClassMemberType.TYPE_UINT16: "int",
    ClassMemberType.TYPE_INT32: "int",
    ClassMemberType.TYPE_UINT32: "int",
    ClassMemberType.TYPE_INT64: "int",
    ClassMemberType.TYPE_UINT64: "int",
    ClassMemberType.TYPE_REAL: "float",
    # ClassMemberType.TYPE_VECTOR4: "hkVector4",
    # ClassMemberType.TYPE_QUATERNION: "hkQuaternionf",
    # ClassMemberType.TYPE_MATRIX3: "hkMatrix3",
    # ClassMemberType.TYPE_ROTATION: "",
    # ClassMemberType.TYPE_QSTRANSFORM: "hkQsTransform",
    # ClassMemberType.TYPE_MATRIX4: "hkMatrix4",
    # ClassMemberType.TYPE_TRANSFORM: "hkTransform",
    # ClassMemberType.TYPE_ZERO: "",
    # ClassMemberType.TYPE_POINTER: "Ptr",
    # ClassMemberType.TYPE_FUNCTIONPOINTER: "",
    ClassMemberType.TYPE_ARRAY: "list",
    # ClassMemberType.TYPE_INPLACEARRAY: "",
    # ClassMemberType.TYPE_ENUM: "hkEnum",
    # ClassMemberType.TYPE_STRUCT: "hkClass",
    # ClassMemberType.TYPE_SIMPLEARRAY: "",
    # ClassMemberType.TYPE_HOMOGENOUSARRAY: "",
    # ClassMemberType.TYPE_VARIANT: "",
    # ClassMemberType.TYPE_CSTRING: "",
    ClassMemberType.TYPE_ULONG: "int",
    # ClassMemberType.TYPE_FLAGS: "hkFlags",
    ClassMemberType.TYPE_HALF: "hkHalf16",
    ClassMemberType.TYPE_STRINGPTR: "str",
    ClassMemberType.TYPE_RELARRAY: "list",
    # ClassMemberType.TYPE_MAX: "",
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

    Also different, but dangerously similar, to the `hkLegacyType` enum class in Havok.

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
    Array = 0b00001000  # 8  # array pointer; also type of `hkPropertyBag` and `hkReflect::Type` in newer Havok
    Struct = 0b00101000  # 40  # fixed-length `T[N]` array
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
    def from_packfile_integer(cls, packfile_type: ClassMemberType) -> int:
        """Construct flags from given `ClassMemberType`.

        Raises a `TypeError` if called on non-integer type.
        """
        if packfile_type == ClassMemberType.TYPE_UINT8:
            return cls.Int | cls.Int8
        elif packfile_type == ClassMemberType.TYPE_INT8:
            return cls.Int | cls.Int8 | cls.IsSigned
        elif packfile_type == ClassMemberType.TYPE_UINT16:
            return cls.Int | cls.Int16
        elif packfile_type == ClassMemberType.TYPE_INT16:
            return cls.Int | cls.Int16 | cls.IsSigned
        elif packfile_type == ClassMemberType.TYPE_UINT32:
            return cls.Int | cls.Int32
        elif packfile_type == ClassMemberType.TYPE_INT32:
            return cls.Int | cls.Int32 | cls.IsSigned
        elif packfile_type == ClassMemberType.TYPE_UINT64:
            return cls.Int | cls.Int64
        elif packfile_type == ClassMemberType.TYPE_INT64:
            return cls.Int | cls.Int64 | cls.IsSigned
        else:
            raise TypeError(f"Given `ClassMemberType` is not an integer type: {packfile_type.name}")

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
    """Bit flags indicating which types of data are stored in a tagfile `TypeInfo` as variable ints."""

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
