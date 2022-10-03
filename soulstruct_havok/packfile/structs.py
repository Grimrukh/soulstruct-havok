from __future__ import annotations

__all__ = [
    "PackFileTypeItem",
    "PackFileItemEntry",
    "PackFileHeader",
    "PackFileHeaderExtension",
    "PackFileSectionHeader",
    "PackFileVersion",
    "PackfileHeaderInfo",
    "CHILD_POINTER_STRUCT",
    "ITEM_POINTER_STRUCT",
    "ITEM_SPEC_STRUCT",
    "TYPE_NAME_HASHES",
]

import abc
import typing as tp
from enum import IntEnum

from soulstruct.utilities.binary import BinaryStruct, BinaryObject, BinaryReader, BinaryWriter

if tp.TYPE_CHECKING:
    from collections import deque
    from soulstruct_havok.types.core import hk, hkArray_, Ptr_


class PackFileBaseEntry(abc.ABC):
    local_data_offset: int
    entry_byte_size: int
    raw_data: bytes

    child_pointers: dict[int, int]  # maps source offset to dest offset inside same entry
    item_pointers: dict[int, tuple[PackFileBaseEntry, int]]  # maps source offset to dest entry from same section
    hk_type: tp.Optional[tp.Type[hk | hkArray_ | Ptr_]]

    reader: tp.Optional[BinaryReader]
    writer: tp.Optional[BinaryWriter]

    def __init__(self):
        self.local_data_offset = -1
        self.entry_byte_size = -1
        self.raw_data = b""
        self.child_pointers = {}
        self.item_pointers = {}
        self.hk_type = None
        self.reader = None
        self.writer = None

    def unpack(self, section_reader: BinaryReader, data_size: int):
        """`reader` should contain the given section data only (so offset 0 is the section start)."""
        self.local_data_offset = section_reader.position  # offset inside data section
        self.entry_byte_size = data_size
        self.raw_data = section_reader.read(data_size)  # parsed later

    def get_offset_in_entry(self, offset: int) -> int:
        """Returns given offset relative to the start of this entry, if it is inside this entry.

        Otherwise, returns -1.
        """
        if self.local_data_offset <= offset < self.local_data_offset + self.entry_byte_size:
            return offset - self.local_data_offset
        return -1

    def start_reader(self):
        """Create raw data reader. Raises `ValueError` if the reader was already created."""
        if self.reader is not None:
            raise ValueError(f"`{self.__class__.__name__}` reader was already created.")
        self.reader = BinaryReader(self.raw_data)

    def start_writer(self):
        if self.writer is not None:
            raise ValueError(f"`{self.__class__.__name__}` writer was already created.")
        self.writer = BinaryWriter()


class PackFileTypeItem(PackFileBaseEntry):

    TYPE_STRUCT_32 = BinaryStruct(
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

    TYPE_STRUCT_64 = BinaryStruct(
        ("name_pointer", "Q", 0),  # child pointer
        ("parent_pointer", "Q", 0),  # entry pointer
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

    ENUM_TYPE_STRUCT_32 = BinaryStruct(
        ("name_pointer", "I", 0),  # child pointer
        ("items_pointer", "I", 0),  # child pointer
        ("items_count", "I"),
        ("attributes_pointer", "I"),
        ("flags", "I"),
        # 12 bytes of padding here in actual type entries (16 align), but no padding in "embedded" enums inside types.
    )

    ENUM_TYPE_STRUCT_64 = BinaryStruct(
        ("enum_name_pointer", "Q", 0),  # child pointer
        ("items_pointer", "Q", 0),  # child pointer
        ("items_count", "I"),
        ("attributes_pointer", "Q"),
        ("flags", "I"),
        # 12 bytes of padding here in actual type entries (16 align), but no padding in "embedded" enums inside types.
    )

    MEMBER_TYPE_STRUCT_32 = BinaryStruct(
        ("name_pointer", "I", 0),  # child pointer
        ("type_pointer", "I", 0),  # entry pointer
        ("enum_pointer", "I", 0),  # entry pointer
        ("member_type", "B"),
        ("member_subtype", "B"),
        ("c_array_size", "H"),  # usually zero
        ("flags", "H"),
        ("offset", "H"),
        ("attributes_pointer", "I"),  # never observed; assuming this never occurs
    )

    MEMBER_TYPE_STRUCT_64 = BinaryStruct(
        ("name_pointer", "Q", 0),  # child pointer
        ("type_pointer", "Q", 0),  # entry pointer
        ("enum_pointer", "Q", 0),  # entry pointer
        ("member_type", "B"),
        ("member_subtype", "B"),
        ("c_array_size", "H"),  # size of tuple T[N]; usually zero
        ("flags", "H"),
        ("offset", "H"),
        ("attributes_pointer", "Q"),  # never observed; assuming this never occurs
    )

    GENERIC_TYPE_NAMES = ["hkArray", "hkEnum", "hkRefPtr", "hkViewPtr", "T*", "T[N]"]

    item_pointers: dict[int, tuple[PackFileTypeItem, int]]

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

    def get_referenced_type_item(self, offset: int) -> tp.Optional[PackFileTypeItem]:
        """Look for `self.item_pointers[offset]` and recover the pointed `PackFileTypeItem`."""
        if offset in self.item_pointers:
            type_item, zero = self.item_pointers[offset]
            if zero != 0:
                raise AssertionError(f"Found type item pointer placeholder other than zero: {zero}")
            return type_item
        # Member is not a class or pointer.
        return None

    def __repr__(self):
        return f"PackFileTypeEntry({self.get_type_name()})"


class PackFileItemEntry(PackFileBaseEntry):

    item_pointers: dict[int, tuple[PackFileItemEntry, int]]
    hk_type: tp.Type[hk | hkArray_ | Ptr_]
    value: None | hk | bool | int | float | list | tuple
    pending_rel_arrays: list[deque[tp.Callable]]  # Class-pushed lists of functions that fill in jumps

    def __init__(self, hk_type: tp.Type[hk | hkArray_ | Ptr_]):
        super().__init__()
        self.hk_type = hk_type
        self.value = None
        self.pending_rel_arrays = []

    def get_class_name(self):
        """Get (real) Havok class name for packfile class name section."""
        if self.hk_type.__name__ == "hkRootLevelContainer":
            return "hkRootLevelContainer"
        # Otherwise, item type should be a pointer type.
        try:
            return type(self.value).get_real_name()
        except AttributeError:
            raise ValueError(
                f"Packfile item type is not `hkRootLevelContainer` or a pointer: {type(self.value).__name__}"
            )

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
        ("item_pointers_offset", "I"),
        ("item_specs_offset", "I"),
        ("exports_offset", "I"),
        ("imports_offset", "I"),
        ("end_offset", "I"),
    )

    section_tag: bytes
    absolute_data_start: int
    child_pointers_offset: int
    item_pointers_offset: int
    item_specs_offset: int
    exports_offset: int
    imports_offset: int
    end_offset: int

    def pack(self, writer: BinaryWriter):
        writer.pack_struct(
            self.STRUCT,
            self,
            absolute_data_start=writer.AUTO_RESERVE,
            child_pointers_offset=writer.AUTO_RESERVE,
            item_pointers_offset=writer.AUTO_RESERVE,
            item_specs_offset=writer.AUTO_RESERVE,
            exports_offset=writer.AUTO_RESERVE,
            imports_offset=writer.AUTO_RESERVE,
            end_offset=writer.AUTO_RESERVE,
        )

    def fill_type_name_or_type_section(self, writer: BinaryWriter, absolute_data_start: int, end_offset: int):
        self.fill(
            writer,
            absolute_data_start=absolute_data_start,
            child_pointers_offset=end_offset,
            item_pointers_offset=end_offset,
            item_specs_offset=end_offset,
            exports_offset=end_offset,
            imports_offset=end_offset,
            end_offset=end_offset,
        )


class PackfileHeaderInfo(tp.NamedTuple):
    """Minimal info needed to pack a packfile. Stored in `HKX` and must be passed to `PackFileUnpacker`."""
    header_version: PackFileVersion
    pointer_size: int
    is_little_endian: bool
    padding_option: int
    contents_version_string: bytes
    flags: int
    header_extension: None | PackFileHeaderExtension = None  # optional (version 0x0B only)


CHILD_POINTER_STRUCT = BinaryStruct(
    ("source_offset", "I"),
    ("dest_offset", "I"),
)

ITEM_POINTER_STRUCT = BinaryStruct(
    ("source_offset", "I"),
    ("dest_section_index", "I"),  # usually 2 (__data__)
    ("dest_offset", "I"),  # usually zero
)

ITEM_SPEC_STRUCT = BinaryStruct(
    ("local_data_offset", "I"),  # relative offset into "__data__" section
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
