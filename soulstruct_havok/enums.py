from __future__ import annotations

__all__ = ["PackMemberType", "HKXTagFileType", "TagDataType", "TagFormatFlags"]

from enum import IntEnum
from pathlib import Path

from soulstruct.utilities.binary import BinaryReader


class PackMemberType(IntEnum):
    """Indicates data type of a `packfile` type's member, as indicated in files containing HK type definitions.

    These are explicitly just references to Havok primitives that are not defined in any packfiles. The primitive
    types can be looked up from a full `HKXTypeList` by these enum names directly.

    Type is always unique - that is, these are not bit flags that can be combined.

    For `hkRefPtr`, `hkArray`, and `hkEnum` types, a second byte will indicate the type of that pointer/array or the
    size of that enum.
    """

    void = 0b00000000
    hkBool = 0b00000001
    # TODO: 0b00000010 has not appeared.
    hkInt8 = 0b00000011
    hkUint8 = 0b00000100
    hkInt16 = 0b00000101
    hkUint16 = 0b00000110
    hkInt32 = 0b00000111
    hkUint32 = 0b00001000
    hkInt64 = 0b00001001  # TODO: has not appeared in any file, but seems very likely
    hkUint64 = 0b00001010
    hkReal = 0b00001011  # TODO: `float` itself also used once by non-primitive: hkxMeshSection["linearKeyFrameHints"]
    hkVector4 = 0b00001100
    hkQuaternionf = 0b00001101
    hkMatrix3 = 0b00001110
    hkQsTransform = 0b00010000  # translation, rotation, and scale
    hkTransform = 0b00010010  # rotation and translation
    hkMatrix4 = 0b00010001

    Ptr = 0b00010100  # pointer to a single object (either Class or Void)
    hkArray = 0b00010110  # array subtype is in second byte
    hkEnum = 0b00011000  # always has a "hkClassEnum" entry pointer - enum int size in second byte
    hkClass = 0b00011001  # always has a "hkClass" entry pointer - no subtype
    hkUlong = 0b00011110  # distinct from UInt64 and "guaranteed to be the same size as a pointer" (rare)
    hkHalf16 = 0b00100000  # used by `hkpMaterial["rollingFrictionMultiplier"]`. Name found in DSR ragdoll file.
    hkStringPtr = 0b00100001

    # TODO: These appear in BB/DS3 (2014).

    NewStruct = 0b00100010  # name by me
    hkFlags = 0b00011111  # TODO: e.g. member "flags" of `hknpShape`, subtype `hkUint16`
    # 0b00000110_00011111

    @classmethod
    def get_data_type(cls, type_int: int) -> PackMemberType:
        return cls(type_int & 0xFF)

    @classmethod
    def get_pointer_type(cls, type_int: int) -> PackMemberType:
        return cls(type_int >> 8)


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
    Void = 0b00000000  # 0
    Invalid = 0b00000001  # 1
    Bool = 0b00000010  # 2
    String = 0b00000011  # 3
    Int = 0b00000100  # 4
    Float = 0b00000101  # 5
    Pointer = 0b00000110  # 6
    Class = 0b00000111  # 7
    Array = 0b00001000  # 8
    Struct = 0b00101000  # 40

    NewString = 0b10000011  # 131  # TODO: type of 2018 `hkStringPtr`, rather than `String` above

    # SECOND BYTE

    # NOTE: `Struct` subtypes use the second byte to indicate their length. I assume this means their maximum length is
    # 255, though they may just continue to use higher bits.

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

    def has_flag(self, tagfile_types: int):
        return bool(tagfile_types & self.value)

    @classmethod
    def from_packfile_integer(cls, packfile_type: PackMemberType) -> int:
        """Construct flags from given `PackMemberType`.

        Raises a `TypeError` if called on non-integer type.
        """
        if packfile_type == PackMemberType.hkUint8:
            return cls.Int | cls.Int8
        elif packfile_type == PackMemberType.hkInt8:
            return cls.Int | cls.Int8 | cls.IsSigned
        elif packfile_type == PackMemberType.hkUint16:
            return cls.Int | cls.Int16
        elif packfile_type == PackMemberType.hkInt16:
            return cls.Int | cls.Int16 | cls.IsSigned
        elif packfile_type == PackMemberType.hkUint32:
            return cls.Int | cls.Int32
        elif packfile_type == PackMemberType.hkInt32:
            return cls.Int | cls.Int32 | cls.IsSigned
        elif packfile_type == PackMemberType.hkUint64:
            return cls.Int | cls.Int64
        elif packfile_type == PackMemberType.hkInt64:
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
            fmt = f"<{count}H"
        elif tagfile_types & cls.Int32:
            fmt = f"<{count}I"
        elif tagfile_types & cls.Int64:
            fmt = f"<{count}Q"  # This was "<q" in TagTools, which I am 80% sure was a mistake.
        else:
            raise TypeError(f"Cannot get struct format for node sub-type flags {tagfile_types}.")
        return fmt.lower() if tagfile_types & cls.IsSigned or signed else fmt

    def get_primitive_type_hint(self) -> str:
        if self == self.Bool:
            return "bool"
        if self == self.String:
            return "str"
        if self == self.Int:
            return "int"
        if self == self.Float:
            return "float"
        return ""


class TagFormatFlags(IntEnum):
    """Flags indicating which types of data are stored with a `HKXType` in a tagfile, as variable ints."""

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


class TagMemberFlags(IntEnum):
    """Flags indicating properties of a member. Only specified in tagfiles."""

    NotSerializable = 0b0000_0001  # 1
    Protected = 0b0000_0010  # 2
    Private = 0b0000_0100  # 4
    Default = 0b0010_0000  # 32 (always enabled)
