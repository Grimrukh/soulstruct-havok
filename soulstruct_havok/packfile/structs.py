from __future__ import annotations

__all__ = [
    "PackFileTypeEntry",
    "PackFileItemEntry",
    "PackFileHeader",
    "PackFileHeaderExtension",
    "PackFileSectionHeader",
    "PackFileVersion",
    "CHILD_POINTER_STRUCT",
    "ENTRY_POINTER_STRUCT",
    "ENTRY_SPEC_STRUCT",
    "TYPE_NAME_HASHES",
]

import abc
import typing as tp
from enum import IntEnum

from soulstruct.utilities.binary import BinaryStruct, BinaryObject, BinaryReader

from soulstruct_havok.types.core import hk, hkArray_, Ptr_

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryWriter


class PackFileBaseEntry(abc.ABC):
    offset_in_section: int
    entry_byte_size: int
    raw_data: bytes

    child_pointers: dict[int, int]  # maps source offset to dest offset inside same entry
    entry_pointers: dict[int, tuple[PackFileBaseEntry, int]]  # maps source offset to dest entry from same section
    hk_type: tp.Optional[tp.Type[hk | hkArray_ | Ptr_]]

    reader: tp.Optional[BinaryReader]
    writer: tp.Optional[BinaryWriter]

    def __init__(self):
        self.offset_in_section = -1
        self.entry_byte_size = -1
        self.raw_data = b""
        self.child_pointers = {}
        self.entry_pointers = {}
        self.hk_type = None
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


class PackFileTypeEntry(PackFileBaseEntry):

    NODE_TYPE_STRUCT_32 = BinaryStruct(
        ("type_name_pointer", "I", 0),  # child pointer
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
        ("type_name_pointer", "Q", 0),  # child pointer
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
        ("member_super_and_data_types", "H"),  # two `(data_type, pointer_type)` bytes interpreted together
        ("c_array_size", "H"),  # usually zero
        ("flags", "H"),
        ("member_byte_offset", "H"),
        ("custom_attributes_pointer", "I"),  # never observed; assuming this never occurs
    )

    NODE_TYPE_MEMBER_STRUCT_64 = BinaryStruct(
        ("member_name_pointer", "Q", 0),  # child pointer
        ("member_type_pointer", "Q", 0),  # entry pointer
        ("enum_pointer", "Q", 0),  # entry pointer
        ("member_super_and_data_types", "H"),  # two `(data_type, pointer_type)` bytes interpreted together
        ("c_array_size", "H"),  # size of tuple T[N]; usually zero
        ("flags", "H"),
        ("member_byte_offset", "H"),
        ("custom_attributes_pointer", "Q"),  # never observed; assuming this never occurs
    )

    GENERIC_TYPE_NAMES = ["hkArray", "hkEnum", "hkRefPtr", "hkViewPtr", "T*", "T[N]"]

    entry_pointers: dict[int, tuple[PackFileTypeEntry, int]]

    def __init__(self, class_name: str):
        super().__init__()
        self.class_name = class_name  # e.g. "hkClass"

    def get_type_name(self) -> tp.Optional[str]:
        """Quickly look up type name from raw data."""
        if not self.child_pointers:
            return None
        return BinaryReader(self.raw_data).unpack_string(self.child_pointers[0], encoding="utf-8")

    def get_byte_size(self) -> int:
        return BinaryReader(self.raw_data).unpack_value("I", offset=8)

    def get_referenced_entry_type(self, offset: int) -> tp.Optional[PackFileTypeEntry]:
        if offset in self.entry_pointers:
            type_entry, zero = self.entry_pointers[offset]
            if zero != 0:
                raise AssertionError(f"Found type entry pointer placeholder other than zero: {zero}")
            return type_entry
        # Member is not a class or pointer.
        return None

    def __repr__(self):
        return f"PackFileTypeEntry({self.get_type_name()})"


class PackFileItemEntry(PackFileBaseEntry):

    entry_pointers: dict[int, tuple[PackFileItemEntry, int]]
    hk_type: tp.Type[hk | hkArray_ | Ptr_]
    value: None | hk | bool | int | float | list | tuple

    def __init__(self, hk_type: tp.Type[hk | hkArray_ | Ptr_]):
        super().__init__()
        self.hk_type = hk_type
        self.value = None

    def __repr__(self):
        return f"PackFileItemEntry({self.hk_type.__name__})"


class PackFileVersion(IntEnum):
    Version0x05 = 0x05
    Version0x08 = 0x08
    Version0x09 = 0x09
    Version0x0B = 0x0B

    @property
    def has_header_extension(self):
        return self == self.Version0x0B


class PackFileHeader(BinaryObject):

    STRUCT = BinaryStruct(
        ("magic0", "I", 0x57E0E057),
        ("magic1", "I", 0x10C0C010),
        ("user_tag", "i", 0),
        ("version", "i"),  # 0x05 (Des), 0x08/0x09 (DS1PTDE), 0x0B (BB/DS3/SEK)
        ("pointer_size", "B"),  # 4 or 8
        ("is_little_endian", "?"),  # usually True (post DeS I assume)
        ("padding_option", "B"),  # 0 or 1 (1 in Bloodborne)
        ("base_type", "B", 1),
        ("section_count", "i", 3),
        ("contents_section_index", "i", 2),  # data section
        ("contents_section_offset", "i", 0),  # start of data section
        ("contents_type_name_section_index", "i", 0),  # type name section
        ("contents_type_name_section_offset", "i", 75),  # offset of "hkRootLevelContainer" string in type name section
        ("contents_version_string", "14s"),  # e.g. "hk_2010.2.0-r1"
        "x",
        ("minus_one", "B", 0xFF),
        ("flags", "i"),  # usually 0
    )

    version: PackFileVersion
    pointer_size: int
    is_little_endian: bool
    padding_option: int
    contents_version_string: bytes
    flags: int

    DEFAULTS = {
        "version": PackFileVersion.Version0x08,
    }


class PackFileHeaderExtension(BinaryObject):

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


class PackFileSectionHeader(BinaryObject):

    STRUCT = BinaryStruct(
        ("section_tag", "19s"),  # e.g. "__classnames__" (type section)
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

    def fill_type_name_or_type_section(self, writer: BinaryWriter, absolute_data_start: int, end_offset: int):
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
    ("type_section_index", "I", 0),  # always references type section
    ("type_name_offset", "I"),  # offset into `section_index` above (always type section)
)

# Hashes for Havok types (typically generic) that do not have a hash in the known database XML.
TYPE_NAME_HASHES = {
    "2010": {
        "hkClass": 1968725750,
        "hkClassMember": 1551803586,
        "hkClassEnum": 2318797263,
        "hkClassEnumItem": 3463416428,
        "hkaAnimationBinding": 1726663025,
        "hkaDefaultAnimatedReferenceFrame": 1837491269,
        "hkaSplineCompressedAnimation": 2033115323,
    },
    "2014": {
        "hkClass": 869540739,
        "hkClassMember": 2968495897,
        "hkClassEnum": 2318797263,
        "hkClassEnumItem": 3463416428,
    }
}
