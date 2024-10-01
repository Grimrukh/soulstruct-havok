from __future__ import annotations

__all__ = ["PackFileUnpacker"]

import logging
import typing as tp
from dataclasses import dataclass, field
from types import ModuleType

import colorama

from soulstruct.utilities.binary import BinaryReader, ByteOrder

from soulstruct_havok.types import hk550, hk2010, hk2014, hk2015, hk2016, hk2018
from soulstruct_havok.types.hk import hk
from soulstruct_havok.types.exceptions import VersionModuleError, TypeNotDefinedError
from soulstruct_havok.types.info import TypeInfo, get_py_name

from .structs import *
from .type_unpacker import PackFileTypeUnpacker

_LOGGER = logging.getLogger("soulstruct_havok")

colorama.just_fix_windows_console()
R = colorama.Fore.RED
X = colorama.Fore.RESET

ROOT_TYPING = tp.Union[
    None,
    hk550.hkRootLevelContainer,
    hk2010.hkRootLevelContainer,
    hk2014.hkRootLevelContainer,
    hk2015.hkRootLevelContainer,
    hk2016.hkRootLevelContainer,
    hk2018.hkRootLevelContainer,
]


class SectionInfo(tp.NamedTuple):
    """Convenient container for information about a section."""
    raw_data: bytes
    child_pointers: list[ChildPointerStruct]
    item_pointers: list[ItemPointerStruct]
    item_specs: list[ItemSpecStruct]
    end_offset: int


@dataclass(slots=True)
class PackFileUnpacker:
    """Manages a single `HKX` packfile unpacking operation.

    Not all packfiles contain type information, so the unpacker will attempt to use existing type information for them.
    """

    hk_types_module: ModuleType | None = None
    byte_order: ByteOrder = ByteOrder.LittleEndian
    hk_version: str = ""
    header: PackFileHeader | None = None
    header_extension: PackFileHeaderExtension | None = None

    type_items: list[PackFileTypeItem] = field(default_factory=list)
    hk_type_infos: list[TypeInfo] = field(default_factory=list)
    class_names: dict[int, str] = field(default_factory=dict)  # maps class name offsets to names
    class_hashes: dict[str, int] = field(default_factory=dict)  # maps class names to hashes
    data_items: list[PackFileDataItem] = field(default_factory=list)
    root: ROOT_TYPING = None

    def unpack(self, reader: BinaryReader, types_only=False):

        self.byte_order = reader.default_byte_order = ByteOrder.big_endian_bool(
            not reader.unpack_value("?", offset=0x11)
        )
        self.header = PackFileHeader.from_bytes(reader)

        self.hk_version = self.header.contents_version_string.decode()
        _LOGGER.info(
            f"Unpacking packfile with hk version: {self.hk_version} "
            f"({self.byte_order.name}, pointer size = {self.header.pointer_size})")

        if self.header.version.has_header_extension:
            self.header_extension = PackFileHeaderExtension.from_bytes(reader)
            reader.seek(self.header_extension.section_offset + 0x40)
        elif reader.unpack_value("I") != 0xFFFFFFFF:
            raise ValueError(f"Expected 0xFFFFFFFF after packfile header (version {hex(self.header.version)}).")

        if self.header.pointer_size not in {4, 8}:
            raise ValueError(f"Packfile pointer size must be 4 or 8, not {self.header.pointer_size}.")

        class_name_info = self.unpack_section(reader)
        if class_name_info.child_pointers:
            raise AssertionError("'classnames' section has child pointers. Not expected!")
        if class_name_info.item_pointers:
            raise AssertionError("'classnames' section has item pointers. Not expected!")
        if class_name_info.item_specs:
            raise AssertionError("'classnames' section has items. Not expected!")
        self.unpack_class_names(class_name_info.raw_data)

        type_section_info = self.unpack_section(reader)
        for type_section_item_pointer in type_section_info.item_pointers:
            if type_section_item_pointer.dest_section_index != 1:
                raise AssertionError("'types' section has an item pointer with destination section index != -1.")

        data_section_info = self.unpack_section(reader)

        self.type_items = self.unpack_type_items(
            BinaryReader(type_section_info.raw_data, default_byte_order=self.byte_order),
            item_specs=type_section_info.item_specs,
            section_end_offset=type_section_info.end_offset
        )
        self.localize_pointers(
            self.type_items,
            type_section_info.child_pointers,
            type_section_info.item_pointers,
        )

        if self.type_items:
            _LOGGER.info("Found type items in packfile (rare).")
            # Types defined inside file, minus some primitive types that are supplied manually.
            type_unpacker = PackFileTypeUnpacker(
                self.type_items, self.class_hashes, self.header.pointer_size, self.hk_types_module
            )
            self.hk_type_infos = type_unpacker.get_type_infos()
        else:
            self.hk_type_infos = []
            _LOGGER.info("No type entries in packfile (as usual).")

        if types_only:
            return

        if self.hk_version.startswith("Havok-5.5.0"):
            self.hk_types_module = hk550
        elif self.hk_version.startswith("hk_2010"):
            self.hk_types_module = hk2010
        elif self.hk_version.startswith("hk_2014"):
            self.hk_types_module = hk2014
        elif self.hk_version.startswith("hk_2015"):
            self.hk_types_module = hk2015
        elif self.hk_version.startswith("hk_2016"):
            self.hk_types_module = hk2016
        elif self.hk_version.startswith("hk_2018"):
            self.hk_types_module = hk2018
        else:
            raise VersionModuleError(f"No Havok type module for version: {self.hk_version}")

        self.data_items = self.unpack_data_items(
            BinaryReader(data_section_info.raw_data, default_byte_order=self.byte_order),
            item_specs=data_section_info.item_specs,
            section_end_offset=data_section_info.end_offset,
        )
        self.localize_pointers(
            self.data_items,
            data_section_info.child_pointers,
            data_section_info.item_pointers,
        )

        for item in self.data_items:
            # Prepare pointers for consumption, so we can detect unused ones and raise an error.
            item.prepare_pointers()

        root_item = self.data_items[0]
        if root_item.hk_type != self.hk_types_module.hkRootLevelContainer:
            raise TypeError(f"First data item in HKX was not `hkRootLevelContainer`: {root_item.get_class_name()}")
        root_item.start_reader()
        with hk.set_types_dict(self.hk_types_module):
            self.root = self.hk_types_module.hkRootLevelContainer.unpack_packfile(root_item)

        # Check for unused pointers.
        for item in self.data_items:
            if item.remaining_child_pointers:
                item.print_item_dump()
                print(f"Remaining child pointers for item `{item.get_class_name()}`:")
                for k, v in item.all_child_pointers.items():
                    print(f"    {R if k in item.remaining_child_pointers else X}{hex(k)} -> {hex(v)}{X}")
                raise ValueError(f"Item `{item.get_class_name()}` has remaining child pointers. See red in printout.")
            if item.remaining_item_pointers:
                item.print_item_dump()
                print(f"Remaining item pointers for item `{item.get_class_name()}`:")
                for k, v in item.all_item_pointers.items():
                    print(f"    {R if k in item.remaining_item_pointers else X}{hex(k)} -> {v}{X}")
                raise ValueError(f"Item `{item.get_class_name()}` has remaining item pointers. See red in printout.")

    @staticmethod
    def localize_pointers(
        items: list[PackFileTypeItem] | list[PackFileDataItem],
        child_pointers: list[ChildPointerStruct],
        item_pointers: list[ItemPointerStruct],
    ):
        """Resolve pointers and attach them to their source items."""
        for child_pointer in child_pointers:
            # Find source item and offset local to its data.
            for item in items:
                if (item_source_offset := item.get_offset_in_item(child_pointer.source_offset)) != -1:
                    # Check that source object is also dest object.
                    if (item_dest_offset := item.get_offset_in_item(child_pointer.dest_offset)) == -1:
                        raise ValueError("Child pointer source object must be destination object.")
                    item.all_child_pointers[item_source_offset] = item_dest_offset
                    break
            else:
                raise ValueError(f"Could not find source/dest items of child pointer: {child_pointer}.")

        for item_pointer in item_pointers:
            for item in items:
                if (item_source_offset := item.get_offset_in_item(item_pointer.source_offset)) != -1:
                    source_item = item
                    break
            else:
                raise ValueError(f"Could not find source item of item pointer: {item_pointer}.")
            for item in items:
                if (item_dest_offset := item.get_offset_in_item(item_pointer.dest_offset)) != -1:
                    source_item.all_item_pointers[item_source_offset] = (item, item_dest_offset)
                    break
            else:
                raise ValueError(f"Could not find dest item of item pointer: {item_pointer}.")

    def unpack_section(self, reader: BinaryReader) -> SectionInfo:
        """Section structure is:

            - Packed section data (e.g. class name strings or packed entries).
            -
        """
        section = PackFileSectionHeader.from_bytes(reader)

        if self.hk_version.startswith("hk_2014"):
            if reader.read(16).strip(b"\xFF"):
                raise AssertionError("Expected sixteen 0xFF bytes after section header in HKX packfile version 2014.")

        absolute_data_start = section.absolute_data_start
        section_data_end = section.child_pointers_offset
        section_data = reader.unpack_bytes(length=section_data_end, offset=absolute_data_start, strip=False)
        child_pointer_count = (section.item_pointers_offset - section.child_pointers_offset) // 8
        item_pointer_count = (section.item_specs_offset - section.item_pointers_offset) // 12
        item_spec_count = (section.exports_offset - section.item_specs_offset) // 12

        child_pointers = []
        item_pointers = []
        item_specs = []

        with reader.temp_offset(offset=absolute_data_start + section.child_pointers_offset):
            for _ in range(child_pointer_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                child_pointers.append(ChildPointerStruct.from_bytes(reader))
        with reader.temp_offset(offset=absolute_data_start + section.item_pointers_offset):
            for _ in range(item_pointer_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                item_pointers.append(ItemPointerStruct.from_bytes(reader))
        with reader.temp_offset(offset=absolute_data_start + section.item_specs_offset):
            for _ in range(item_spec_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                item_specs.append(ItemSpecStruct.from_bytes(reader))

        return SectionInfo(section_data, child_pointers, item_pointers, item_specs, section_data_end)

    def unpack_class_names(self, class_name_data: bytes):
        """Constructs dictionaries mapping offsets (within class name section) to HKX class names and signatures."""
        self.class_names = {}
        self.class_hashes = {}

        class_name_reader = BinaryReader(class_name_data, default_byte_order=self.byte_order)
        class_name_data_length = len(class_name_data)

        # Continue unpacking class names until end of reader or '\xFF' padding begins.
        while class_name_reader.position != class_name_data_length and class_name_reader.peek_value("H") != 0xFFFF:
            hsh = class_name_reader.unpack_value("I")
            class_name_reader.unpack_value("B", asserted=0x09)  # \t (tab character)
            type_name_offset = class_name_reader.position
            type_name = class_name_reader.unpack_string(encoding="ascii")  # NOTE: these don't have '::' separates, etc.
            self.class_names[type_name_offset] = type_name
            self.class_hashes[type_name] = hsh
            # TODO: Hashes are checked in `TypeInfo` with everything else.

    def unpack_type_items(
        self,
        type_section_reader: BinaryReader,
        item_specs: list[ItemSpecStruct],
        section_end_offset: int,
    ) -> list[PackFileTypeItem]:
        """Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on write.
        """
        type_items = []
        for i, item_spec in enumerate(item_specs):
            class_name = self.class_names[item_spec.type_name_offset]

            if i < len(item_specs) - 1:
                data_size = item_specs[i + 1].local_data_offset - item_spec.local_data_offset
            else:
                data_size = section_end_offset - item_spec.local_data_offset

            type_section_reader.seek(item_spec.local_data_offset)
            type_item = PackFileTypeItem(class_name=class_name)
            type_item.unpack(
                type_section_reader,
                data_size=data_size,
                byte_order=self.byte_order,
                long_varints=self.header.pointer_size == 8,
            )
            type_items.append(type_item)

        return type_items

    def unpack_data_items(
        self,
        data_section_reader: BinaryReader,
        item_specs: list[ItemSpecStruct],
        section_end_offset: int,
    ) -> list[PackFileDataItem]:
        """Assign `raw_data` to each packfile item.

        NOTE: Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on `pack()`.
        """
        data_entries = []
        missing_type_infos = {}  # type: dict[str, tuple[str, TypeInfo | None]]
        for i, item_spec in enumerate(item_specs):
            type_name = self.class_names[item_spec.type_name_offset]
            type_py_name = get_py_name(type_name)
            try:
                hk_type = getattr(self.hk_types_module, type_py_name)
            except AttributeError:
                if type_py_name not in missing_type_infos:
                    # Missing type. Print `TypeInfo` below.
                    type_info_matches = [t for t in self.hk_type_infos[1:] if t.name == type_name]
                    if not type_info_matches:
                        # No type info in file.
                        missing_type_infos[type_py_name] = (type_name, None)
                    else:
                        type_info = type_info_matches[0]
                        missing_type_infos[type_py_name] = (type_name, type_info)
                        # Recursively check member types.
                        members_to_check = type_info.members.copy()
                        while members_to_check:
                            member_info = members_to_check.pop(0)
                            member_type_py_name = get_py_name(member_info.type_py_name)
                            if (
                                member_info.type_info
                                and member_type_py_name not in self.hk_types_module.__dict__
                                and member_type_py_name not in missing_type_infos
                            ):
                                missing_type_infos[member_type_py_name] = (
                                    member_info.type_info.name, member_info.type_info
                                )
                                for member_member_info in member_info.type_info.members:
                                    members_to_check.append(member_member_info)

                continue  # error will be raised below; skip data loading

            if i < len(item_specs) - 1:
                data_size = item_specs[i + 1].local_data_offset - item_spec.local_data_offset
            else:
                data_size = section_end_offset - item_spec.local_data_offset

            data_section_reader.seek(item_spec.local_data_offset)
            data_item = PackFileDataItem(hk_type=hk_type)
            data_item.unpack(
                data_section_reader,
                data_size=data_size,
                byte_order=self.byte_order,
                long_varints=self.header.pointer_size == 8,
            )
            data_entries.append(data_item)

        if missing_type_infos:
            for type_py_name, (type_name, type_info) in missing_type_infos.items():
                if type_info:
                    print(f"Type `{type_py_name}` (real name `{type_name}`) is unknown, but its type data was found:")
                    print(type_info)
                else:
                    print(f"Type `{type_py_name}` (real name `{type_name}`) is unknown and no type data was found.")
            py_names = ", ".join(f"`{type_py_name}`" for type_py_name in missing_type_infos)
            raise TypeNotDefinedError(f"Types {py_names} are unknown. See above for info to generate Python classes.")

        return data_entries

    def get_header_info(self) -> PackfileHeaderInfo:
        if not self.header:
            raise ValueError("`PackFileUnpacker` header has not been set yet.")
        return PackfileHeaderInfo(
            header_version=self.header.version,
            pointer_size=self.header.pointer_size,
            is_little_endian=self.header.is_little_endian,
            padding_option=self.header.padding_option,
            contents_version_string=self.header.contents_version_string,
            flags=self.header.flags,
            header_extension=self.header_extension,
        )

    def raw_repr(self):
        lines = ["Entries:"]
        for item in self.data_items:
            lines.append(f"    Type: {item.hk_type.__name__}")
            lines.append(
                f"        Location: ["
                f"{hex(item.local_data_offset)} - {hex(item.local_data_offset + item.item_byte_size)}"
                f"]"
            )
            lines.append(f"        Child pointers ({len(item.all_child_pointers)}):")
            for ref_source, ref_dest in item.all_child_pointers.items():
                lines.append(f"            Local Offset: {ref_source} -> {ref_dest}")
            lines.append(f"        Entry pointers ({len(item.all_item_pointers)}):")
            for ref_source, (dest_item, ref_dest) in item.all_item_pointers.items():
                lines.append(f"            Global Offset: {ref_source} -> {ref_dest} ({dest_item.hk_type.__name__})")
            lines.append(f"        Raw data length: {len(item.raw_data)}")
        return "\n".join(lines)
