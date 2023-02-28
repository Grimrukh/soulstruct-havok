from __future__ import annotations

__all__ = [
    "PackFileTypeItem",
    "PackFileItemEntry",
    "PackFileHeader",
    "PackFileHeaderExtension",
    "PackFileSectionHeader",
    "PackFileVersion",
    "PackfileHeaderInfo",
    "ChildPointerStruct",
    "ItemPointerStruct",
    "ItemSpecStruct",
    "TYPE_NAME_HASHES",
]

import abc
import typing as tp
from dataclasses import dataclass, field
from enum import IntEnum

from soulstruct.utilities.binary import *

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


@dataclass(slots=True)
class PackFileTypeItem(PackFileBaseEntry):

    class TYPE_STRUCT_32(BinaryStruct):
        type_name_pointer: uint = field(init=False, **Binary(asserted=0))  # child pointer
        parent_type_pointer: uint = field(init=False, **Binary(asserted=0))  # entry pointer
        byte_size: uint
        interface_count: uint
        enums_pointer: uint = field(init=False, **Binary(asserted=0))  # child pointer (NOT an entry pointer to enum!)
        enums_count: uint
        member_pointer: uint = field(init=False, **Binary(asserted=0))  # child pointer
        member_count: uint
        defaults: uint  # child pointer
        flags: uint  # always zero so far in packfiles (could be padding!)
        version: uint  # always zero so far in packfiles (could be padding!)

    class TYPE_STRUCT_64(BinaryStruct):
        """NOTE: Differences are not entirely just `varint` size."""
        type_name_pointer: ulong = field(init=False, **Binary(asserted=0))  # child pointer
        parent_type_pointer: ulong = field(init=False, **Binary(asserted=0))  # entry pointer
        byte_size: uint
        interface_count: uint
        enums_pointer: ulong = field(init=False, **Binary(asserted=0))  # child pointer (NOT an entry pointer to enum!)
        enums_count: uint
        _pad1: bytes = field(init=False, **BinaryPad(4))  # TODO: padding could be earlier (but after byte size)
        member_pointer: ulong = field(init=False, **Binary(asserted=0))  # child pointer
        member_count: uint
        defaults: uint  # child pointer
        flags: uint  # always zero so far in packfiles (could be padding!)
        _pad2: bytes = field(init=False, **BinaryPad(16))  # TODO: padding could be earlier (but after member count)
        version: uint  # always zero in 2010

    class ENUM_TYPE_STRUCT(BinaryStruct):
        name_pointer: varuint = field(init=False, **Binary(asserted=0))  # child pointer
        items_pointer: varuint = field(init=False, **Binary(asserted=0))  # child pointer
        items_count: uint
        attributes_pointer: varuint
        flags: uint
        # 12 bytes of padding here in actual type entries (16 align), but no padding in "embedded" enums inside types.

    class MEMBER_TYPE_STRUCT(BinaryStruct):
        name_pointer: varuint = field(init=False, **Binary(asserted=0))  # child pointer
        type_pointer: varuint = field(init=False, **Binary(asserted=0))  # entry pointer
        enum_pointer: varuint = field(init=False, **Binary(asserted=0))  # entry pointer
        member_type: byte
        member_subtype: byte
        c_array_size: ushort  # size of tuple T[N]; usually zero
        flags: ushort
        offset: ushort
        attributes_pointer: varuint  # never observed; assuming this never occurs

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


@dataclass(slots=True)
class PackFileHeader(BinaryStruct):
    """Packfile header structure."""

    magic0: uint = field(init=False, **Binary(asserted=0x57E0E057))
    magic1: uint = field(init=False, **Binary(asserted=0x10C0C010))
    user_tag: int = field(init=False, **Binary(asserted=0))
    version: PackFileVersion = field(**Binary(int))  # 0x05 (Des), 0x08/0x09 (DS1PTDE), 0x0B (BB/DS3/SEK)
    pointer_size: byte  # 4 or 8
    is_little_endian: bool  # usually True (post DeS I assume)
    padding_option: byte  # 0 or 1 (1 in Bloodborne)
    base_type: byte = field(init=False, **Binary(asserted=1))
    section_count: int = field(init=False, **Binary(asserted=3))
    contents_section_index: int = field(init=False, **Binary(asserted=2))  # data section
    contents_section_offset: int = field(init=False, **Binary(asserted=0))  # start of data section
    contents_type_name_section_index: int = field(init=False, **Binary(asserted=0))  # type name section
    contents_type_name_section_offset: int = field(init=False, **Binary(asserted=75))  # 'hkRootLevelContainer' str
    contents_version_string: bytes = field(**BinaryString(14))  # e.g. "hk_2010.2.0-r1"
    _pad1: bytes = field(init=False, **BinaryPad(1))
    _minus_one: byte = field(init=False, **Binary(asserted=0xFF))
    flags: int  # usually 0


@dataclass(slots=True)
class PackFileHeaderExtension(BinaryStruct):
    unk_x3C: short
    section_offset: short
    unk_x40: uint
    unk_x44: uint
    unk_x48: uint
    unk_x4C: uint


# TODO: up to here
@dataclass(slots=True)
class PackFileSectionHeader(BinaryStruct):
    """Packfile section header structure."""
    section_tag: bytes = field(**BinaryString(19))  # e.g. "__classnames__" (type section)
    minus_one: byte = field(init=False, **Binary(asserted=0xFF))
    absolute_data_start: uint
    child_pointers_offset: uint
    item_pointers_offset: uint
    item_specs_offset: uint
    exports_offset: uint
    imports_offset: uint
    end_offset: uint

    def fill_type_name_or_type_section(self, writer: BinaryWriter, absolute_data_start: int, end_offset: int):
        writer.fill("absolute_data_start", absolute_data_start, obj=self)
        for field_name in (
            "child_pointers_offset",
            "item_pointers_offset",
            "item_specs_offset",
            "exports_offset",
            "imports_offset",
            "end_offset",
        ):
            writer.fill(field_name, end_offset, obj=self)


@dataclass(slots=True)
class PackfileHeaderInfo:
    """Minimal info needed to pack a packfile. Stored in `HKX` and must be passed to `PackFileUnpacker`."""
    header_version: PackFileVersion
    pointer_size: int
    is_little_endian: bool
    padding_option: int
    contents_version_string: bytes
    flags: int
    header_extension: None | PackFileHeaderExtension = None  # optional (version 0x0B -- a la Bloodborne -- only)


@dataclass(slots=True)
class ChildPointerStruct(BinaryStruct):
    source_offset: uint
    dest_offset: uint


@dataclass(slots=True)
class ItemPointerStruct(BinaryStruct):
    source_offset: uint
    dest_section_index: uint  # usually 2 (__data__)
    dest_offset: uint  # usually zero


@dataclass(slots=True)
class ItemSpecStruct(BinaryStruct):
    local_data_offset: uint  # relative offset into "__data__" section
    type_section_index: uint = field(init=False, **Binary(asserted=0))  # always references type section
    type_name_offset: uint  # offset into `section_index` above (always type section)


# Hashes for Havok types (typically generic types) that do not have a hash in the known database XML.
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
