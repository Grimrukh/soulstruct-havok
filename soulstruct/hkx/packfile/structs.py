from __future__ import annotations

__all__ = [
    "HKXTypeEntry",
    "HKXItemEntry",
    "HKXHeader",
    "HKXHeaderExtension",
    "HKXSectionHeader",
    "HKXPackFileVersion",
    "CHILD_POINTER_STRUCT",
    "ENTRY_POINTER_STRUCT",
    "ENTRY_SPEC_STRUCT",
    "CLASS_NAME_SIGNATURES",
]

import abc
import typing as tp
from enum import IntEnum

from soulstruct.utilities.binary import BinaryStruct, BinaryObject, BinaryReader

from ..nodes import HKXNode
from ..types import HKXType

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryWriter


class HKXPackBaseEntry(abc.ABC):
    offset_in_section: int
    entry_byte_size: int
    raw_data: bytes

    child_pointers: dict[int, int]  # maps source offset to dest offset inside same entry
    entry_pointers: dict[int, tuple[HKXPackBaseEntry, int]]  # maps source offset to dest entry from same section
    hkx_type: tp.Optional[HKXType]

    reader: tp.Optional[BinaryReader]
    writer: tp.Optional[BinaryWriter]

    def __init__(self):
        self.offset_in_section = -1
        self.entry_byte_size = -1
        self.raw_data = b""
        self.child_pointers = {}
        self.entry_pointers = {}
        self.hkx_type = None
        self.reader = None
        self.writer = None

    def unpack(self, section_reader: BinaryReader, data_size: int):
        """`reader` should contain the given section data only (so offset 0 is the section start)."""
        self.offset_in_section = section_reader.position  # offset inside data section
        self.entry_byte_size = data_size
        self.raw_data = section_reader.read(data_size)  # parsed later

    def get_offset_in_entry(self, offset: int) -> int:
        """Returns given offset relative to the start of this entry, if it is inside this entry.

        Otherwise, returns -1.
        """
        if self.offset_in_section <= offset < self.offset_in_section + self.entry_byte_size:
            return offset - self.offset_in_section
        return -1

    def start_reader(self):
        """Create raw data reader. Raises `ValueError` if the reader was already created."""
        if self.reader is not None:
            raise ValueError(f"`{self.__class__.__name__}` reader was already created.")
        self.reader = BinaryReader(self.raw_data)


class HKXTypeEntry(HKXPackBaseEntry):

    NODE_TYPE_STRUCT_32 = BinaryStruct(
        ("class_name_pointer", "I", 0),  # child pointer
        ("parent_type_pointer", "I", 0),  # entry pointer
        ("byte_size", "I"),
        ("interface_count", "I"),
        ("enums_pointer", "I", 0),  # child pointer (NOT an entry pointer to the actual enum!)
        ("enums_count", "I"),
        ("member_pointer", "I", 0),  # child pointer
        ("member_count", "I"),
        ("defaults", "I"),  # child pointer
        ("flags", "I"),  # always zero so far in packfiles (could be padding!)
        ("version", "I"),  # always zero so far in packfiles (could be padding!)
    )

    NODE_TYPE_STRUCT_64 = BinaryStruct(
        ("class_name_pointer", "Q", 0),  # child pointer
        ("parent_type_pointer", "Q", 0),  # entry pointer
        ("byte_size", "I"),
        ("interface_count", "I"),
        ("enums_pointer", "Q", 0),  # child pointer (NOT an entry pointer to the actual enum!)
        ("enums_count", "I"),
        ("pad1", "I", 0),  # TODO: padding could be earlier (but after byte size). Only zero observed right here.
        ("member_pointer", "Q", 0),  # child pointer
        ("member_count", "I"),
        ("defaults", "I"),  # child pointer
        ("flags", "I"),  # always zero so far in packfiles (could be padding!)
        ("pad2", "4I", (0, 0, 0, 0)),  # TODO: padding could be earlier (but after member count). Only zeroes observed.
        ("version", "I"),  # always zero in 2010
    )

    NODE_TYPE_ENUM_STRUCT_32 = BinaryStruct(
        ("enum_name_pointer", "I", 0),  # child pointer
        ("items_pointer", "I", 0),  # child pointer
        ("items_count", "I"),
        ("custom_attributes_pointer", "I"),
        ("flags", "I"),
        # 12 bytes of padding here in actual type entries (16 align), but no padding in "embedded" enums inside types.
    )

    NODE_TYPE_ENUM_STRUCT_64 = BinaryStruct(
        ("enum_name_pointer", "Q", 0),  # child pointer
        ("items_pointer", "Q", 0),  # child pointer
        ("items_count", "I"),
        ("custom_attributes_pointer", "Q"),
        ("flags", "I"),
        # 12 bytes of padding here in actual type entries (16 align), but no padding in "embedded" enums inside types.
    )

    NODE_TYPE_MEMBER_STRUCT_32 = BinaryStruct(
        ("member_name_pointer", "I", 0),  # child pointer
        ("member_type_pointer", "I", 0),  # entry pointer
        ("enum_pointer", "I", 0),  # entry pointer
        ("member_data_and_pointer_type", "H"),  # two `(data_type, pointer_type)` bytes interpreted together
        ("c_array_size", "H"),  # usually zero
        ("flags", "H"),
        ("member_byte_offset", "H"),
        ("custom_attributes_pointer", "I"),  # never observed; assuming this never occurs
    )

    NODE_TYPE_MEMBER_STRUCT_64 = BinaryStruct(
        ("member_name_pointer", "Q", 0),  # child pointer
        ("member_type_pointer", "Q", 0),  # entry pointer
        ("enum_pointer", "Q", 0),  # entry pointer
        ("member_data_and_pointer_type", "H"),  # two `(data_type, pointer_type)` bytes interpreted together
        ("c_array_size", "H"),  # size of tuple T[N]; usually zero
        ("flags", "H"),
        ("member_byte_offset", "H"),
        ("custom_attributes_pointer", "Q"),  # never observed; assuming this never occurs
    )

    entry_pointers: dict[int, tuple[HKXTypeEntry, int]]

    def __init__(self, class_name: str):
        super().__init__()
        self.class_name = class_name

    def get_type_name(self) -> str:
        return BinaryReader(self.raw_data).unpack_string(self.child_pointers[0], encoding="utf-8")

    def get_byte_size(self) -> int:
        return BinaryReader(self.raw_data).unpack_value("I", offset=8)

    def __repr__(self):
        return f"HKXTypeEntry({self.class_name})"


class HKXItemEntry(HKXPackBaseEntry):

    entry_pointers: dict[int, tuple[HKXItemEntry, int]]
    node: tp.Optional[HKXNode]  # for tracking the corresponding unpacked `HKXNode`

    def __init__(self, hkx_type: HKXType):
        super().__init__()
        self.hkx_type = hkx_type
        self.node = None

    def __repr__(self):
        return f"HKXItemEntry({self.hkx_type.name})"


class HKXPackFileVersion(IntEnum):
    Version0x05 = 0x05
    Version0x08 = 0x08
    Version0x09 = 0x09
    Version0x0B = 0x0B

    @property
    def has_header_extension(self):
        return self == self.Version0x0B


class HKXHeader(BinaryObject):

    STRUCT = BinaryStruct(
        ("magic0", "I", 0x57E0E057),
        ("magic1", "I", 0x10C0C010),
        ("user_tag", "i", 0),
        ("version", "i"),  # 0x05 (Des), 0x08/0x09 (DS1PTDE), 0x0B (BB/DS3/SEK)
        ("pointer_size", "B"),  # 4 or 8
        ("is_little_endian", "?"),  # usually True (post DeS I assume)
        ("padding_option", "B"),  # 0 or 1 (1 in Bloodborne)
        ("base_class", "B", 1),
        ("section_count", "i", 3),
        ("contents_section_index", "i", 2),  # data section
        ("contents_section_offset", "i", 0),  # start of data section
        ("contents_class_name_section_index", "i", 0),  # class name section
        ("contents_class_name_section_offset", "i", 75),  # offset of "hkRootContainer" string in class name section
        ("contents_version_string", "14s"),  # e.g. "hk_2010.2.0-r1"
        "x",
        ("minus_one", "B", 0xFF),
        ("flags", "i"),  # usually 0
    )

    version: HKXPackFileVersion
    pointer_size: int
    is_little_endian: bool
    padding_option: int
    contents_version_string: bytes
    flags: int

    DEFAULTS = {
        "version": HKXPackFileVersion.Version0x08,
    }


class HKXHeaderExtension(BinaryObject):

    STRUCT = BinaryStruct(
        ("unk_x3C", "h"),
        ("section_offset", "h"),
        ("unk_x40", "I"),
        ("unk_x44", "I"),
        ("unk_x48", "I"),
        ("unk_x4C", "I"),
    )

    unk_x3C: int
    section_offset: int
    unk_x40: int
    unk_x44: int
    unk_x48: int
    unk_x4C: int


class HKXSectionHeader(BinaryObject):

    STRUCT = BinaryStruct(
        ("section_tag", "19s"),  # e.g. "__classnames__"
        ("minus_one", "B", 0xFF),
        ("absolute_data_start", "I"),
        ("child_pointers_offset", "I"),
        ("entry_pointers_offset", "I"),
        ("entry_specs_offset", "I"),
        ("exports_offset", "I"),
        ("imports_offset", "I"),
        ("end_offset", "I"),
    )

    section_tag: bytes
    absolute_data_start: int
    child_pointers_offset: int
    entry_pointers_offset: int
    entry_specs_offset: int
    exports_offset: int
    imports_offset: int
    end_offset: int

    def pack(self, writer: BinaryWriter):
        writer.pack_struct(
            self.STRUCT,
            self,
            absolute_data_start=writer.AUTO_RESERVE,
            child_pointers_offset=writer.AUTO_RESERVE,
            entry_pointers_offset=writer.AUTO_RESERVE,
            entry_specs_offset=writer.AUTO_RESERVE,
            exports_offset=writer.AUTO_RESERVE,
            imports_offset=writer.AUTO_RESERVE,
            end_offset=writer.AUTO_RESERVE,
        )

    def fill_classname_or_type_section(self, writer: BinaryWriter, absolute_data_start: int, end_offset: int):
        self.fill(
            writer,
            absolute_data_start=absolute_data_start,
            child_pointers_offset=end_offset,
            entry_pointers_offset=end_offset,
            entry_specs_offset=end_offset,
            exports_offset=end_offset,
            imports_offset=end_offset,
            end_offset=end_offset,
        )


CHILD_POINTER_STRUCT = BinaryStruct(
    ("source_offset", "I"),
    ("dest_offset", "I"),
)

ENTRY_POINTER_STRUCT = BinaryStruct(
    ("source_offset", "I"),
    ("dest_section_index", "I"),  # usually 2 (__data__)
    ("dest_offset", "I"),  # usually zero
)

ENTRY_SPEC_STRUCT = BinaryStruct(
    ("relative_entry_offset", "I"),  # relative offset into "__data__" section
    ("class_section_index", "I", 0),  # always references class section
    ("class_name_offset", "I"),  # offset into `section_index` above (always class section)
)

CLASS_NAME_SIGNATURES = {
    "hkClass": 1968725750,
    "hkClassMember": 1551803586,
    "hkClassEnum": 2318797263,
    "hkClassEnumItem": 3463416428,
    "hkRootLevelContainer": 661831966,
    "hkaAnimationBinding": 1726663025,
    "hkaAnimationContainer": 2378302259,
    "hkaDefaultAnimatedReferenceFrame": 1837491269,
    "hkaRagdollInstance": 357124328,
    "hkaSkeleton": 913211936,
    "hkaSkeletonMapper": 316621477,
    "hkaSplineCompressedAnimation": 2033115323,
    "hkpCapsuleShape": 3708493779,
    "hkpConstraintInstance": 55491167,
    "hkpPhysicsData": 3265552868,
    "hkpPhysicsSystem": 4285680663,
    "hkpPositionConstraintMotor": 1955574531,
    "hkpRagdollConstraintData": 2411060521,
    "hkpRigidBody": 1979242501,
}
