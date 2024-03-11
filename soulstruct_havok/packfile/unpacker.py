from __future__ import annotations

__all__ = ["PackFileUnpacker"]

import logging
import typing as tp
from dataclasses import dataclass, field
from types import ModuleType

from soulstruct.utilities.binary import BinaryReader, ByteOrder

from soulstruct_havok.types import hk2010, hk2014, hk2015, hk2016, hk2018
from soulstruct_havok.types.hk import hk
from soulstruct_havok.types.exceptions import VersionModuleError, TypeNotDefinedError
from soulstruct_havok.types.info import TypeInfo, get_py_name

from .structs import *
from .type_unpacker import PackFileTypeUnpacker

_LOGGER = logging.getLogger("soulstruct_havok")

ROOT_TYPING = tp.Union[
    None,
    hk2010.hkRootLevelContainer,
    hk2014.hkRootLevelContainer,
    hk2015.hkRootLevelContainer,
    hk2016.hkRootLevelContainer,
    hk2018.hkRootLevelContainer,
]

_DEBUG_PRINT = []
_DEBUG_MSG = True
_DEBUG_TYPE_PRINT = False


def _DEBUG(*args, **kwargs):
    if _DEBUG_MSG:
        print(*args, **kwargs)


class SectionInfo(tp.NamedTuple):
    raw_data: bytes
    child_pointers: list[ChildPointerStruct]
    item_pointers: list[EntryPointerStruct]
    entry_specs: list[EntrySpecStruct]
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

    type_entries: list[PackFileType] = field(default_factory=list)
    hk_type_infos: list[TypeInfo] = field(default_factory=list)
    class_names: dict[int, str] = field(default_factory=dict)  # maps class name offsets to names
    class_hashes: dict[str, int] = field(default_factory=dict)  # maps class names to hashes
    item_entries: list[PackFileItem] = field(default_factory=list)
    root: ROOT_TYPING = None

    def unpack(self, reader: BinaryReader, types_only=False):

        self.byte_order = reader.default_byte_order = ByteOrder.big_endian_bool(
            not reader.unpack_value("?", offset=0x11)
        )
        self.header = PackFileHeader.from_bytes(reader)

        self.hk_version = self.header.contents_version_string[3:7].decode()  # from "hk_YYYY" (e.g. "2010")
        _LOGGER.info(f"Unpacking packfile with hk version: {self.hk_version}")

        if self.header.version.has_header_extension:
            self.header_extension = PackFileHeaderExtension.from_bytes(reader)
            reader.seek(self.header_extension.section_offset + 0x40)
        elif reader.unpack_value("I") != 0xFFFFFFFF:
            raise ValueError(f"Expected 0xFFFFFFFF after packfile header (version {hex(self.header.version)}).")

        if self.header.pointer_size not in {4, 8}:
            raise ValueError(f"Packfile pointer size must be 4 or 8, not {self.header.pointer_size}.")

        class_name_info = self.unpack_section(reader)
        if class_name_info.child_pointers:
            raise AssertionError("Type name section has local references. Not expected!")
        if class_name_info.item_pointers:
            raise AssertionError("Type name section has global references. Not expected!")
        if class_name_info.entry_specs:
            raise AssertionError("Type name section has data entries. Not expected!")

        type_section_info = self.unpack_section(reader)
        for type_section_entry_pointer in type_section_info.item_pointers:
            if type_section_entry_pointer.dest_section_index != 1:
                raise AssertionError("type global error")

        data_section_info = self.unpack_section(reader)

        self.unpack_class_names(class_name_info.raw_data)

        self.type_entries = self.unpack_type_entries(
            BinaryReader(type_section_info.raw_data),
            entry_specs=type_section_info.entry_specs,
            section_end_offset=type_section_info.end_offset
        )
        self.localize_pointers(
            self.type_entries,
            type_section_info.child_pointers,
            type_section_info.item_pointers,
        )

        if self.type_entries:
            _LOGGER.info("Found type entries in packfile.")
            # Types defined inside file, minus some primitive types that are supplied manually.
            type_unpacker = PackFileTypeUnpacker(
                self.type_entries, self.class_hashes, self.header.pointer_size, self.hk_types_module
            )
            self.hk_type_infos = type_unpacker.get_type_infos()
        else:
            self.hk_type_infos = []
            _LOGGER.info("No type entries in packfile.")

        if types_only:
            return

        if self.hk_version == "2010":
            from soulstruct_havok.types import hk2010
            self.hk_types_module = hk2010
        elif self.hk_version == "2014":
            from soulstruct_havok.types import hk2014
            self.hk_types_module = hk2014
        elif self.hk_version == "2015":
            from soulstruct_havok.types import hk2015
            self.hk_types_module = hk2015
        elif self.hk_version == "2018":
            from soulstruct_havok.types import hk2018
            self.hk_types_module = hk2018
        else:
            raise VersionModuleError(f"No Havok type module for version: {self.hk_version}")

        self.item_entries = self.unpack_item_entries(
            BinaryReader(data_section_info.raw_data),
            item_entry_specs=data_section_info.entry_specs,
            section_end_offset=data_section_info.end_offset,
        )
        self.localize_pointers(
            self.item_entries,
            data_section_info.child_pointers,
            data_section_info.item_pointers,
        )

        root_entry = self.item_entries[0]
        if root_entry.hk_type != self.hk_types_module.hkRootLevelContainer:
            raise TypeError(f"First data entry in HKX was not root node: {root_entry.hk_type.__name__}")
        root_entry.start_reader()
        with hk.set_types_dict(self.hk_types_module):
            self.root = self.hk_types_module.hkRootLevelContainer.unpack_packfile(root_entry)

    @staticmethod
    def localize_pointers(
        entries: list[PackFileType] | list[PackFileItem],
        child_pointers: list[ChildPointerStruct],
        item_pointers: list[EntryPointerStruct],
    ):
        """Resolve pointers and attach them to their source entry objects."""
        for child_pointer in child_pointers:
            # Find source entry and offset local to its data.
            for entry in entries:
                if (entry_source_offset := entry.get_offset_in_item(child_pointer.source_offset)) != -1:
                    # Check that source object is also dest object.
                    if (entry_dest_offset := entry.get_offset_in_item(child_pointer.dest_offset)) == -1:
                        raise AssertionError("Child pointer source object was NOT dest object. Not expected!")
                    entry.child_pointers[entry_source_offset] = entry_dest_offset
                    break
            else:
                raise ValueError(f"Could not find source/dest entry of child pointer: {child_pointer}.")

        for entry_pointer in item_pointers:
            for entry in entries:
                if (entry_source_offset := entry.get_offset_in_item(entry_pointer.source_offset)) != -1:
                    source_entry = entry
                    break
            else:
                raise ValueError(f"Could not find source entry of entry pointer: {entry_pointer}.")
            for entry in entries:
                if (entry_dest_offset := entry.get_offset_in_item(entry_pointer.dest_offset)) != -1:
                    source_entry.item_pointers[entry_source_offset] = (entry, entry_dest_offset)
                    break
            else:
                raise ValueError(f"Could not find dest entry of entry pointer: {entry_pointer}.")

    def unpack_section(self, reader: BinaryReader) -> SectionInfo:
        """Section structure is:

            - Packed section data (e.g. class name strings or packed entries).
            -
        """
        section = PackFileSectionHeader.from_bytes(reader)

        if self.hk_version == "2014":
            if reader.read(16).strip(b"\xFF"):
                raise AssertionError("Expected sixteen 0xFF bytes after section header in HKX packfile version 2014.")

        absolute_data_start = section.absolute_data_start
        section_data_end = section.child_pointers_offset
        section_data = reader.unpack_bytes(length=section_data_end, offset=absolute_data_start, strip=False)
        child_pointer_count = (section.item_pointers_offset - section.child_pointers_offset) // 8
        entry_pointer_count = (section.item_specs_offset - section.item_pointers_offset) // 12
        entry_spec_count = (section.exports_offset - section.item_specs_offset) // 12

        child_pointers = []
        item_pointers = []
        entry_specs = []

        with reader.temp_offset(offset=absolute_data_start + section.child_pointers_offset):
            for _ in range(child_pointer_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                child_pointers.append(ChildPointerStruct.from_bytes(reader))
        with reader.temp_offset(offset=absolute_data_start + section.item_pointers_offset):
            for _ in range(entry_pointer_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                item_pointers.append(EntryPointerStruct.from_bytes(reader))
        with reader.temp_offset(offset=absolute_data_start + section.item_specs_offset):
            for _ in range(entry_spec_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                entry_specs.append(EntrySpecStruct.from_bytes(reader))

        return SectionInfo(section_data, child_pointers, item_pointers, entry_specs, section_data_end)

    def unpack_class_names(self, class_name_data: bytes):
        """Constructs dictionaries mapping offsets (within class name section) to HKX class names and signatures."""
        self.class_names = {}
        self.class_hashes = {}

        class_name_reader = BinaryReader(class_name_data)
        class_name_data_length = len(class_name_data)

        # Continue unpacking class names until end of reader or '\xFF' padding begins.
        while class_name_reader.position != class_name_data_length and class_name_reader.peek_value("H") != 0xFFFF:
            hsh = class_name_reader.unpack_value("I")
            class_name_reader.unpack_value("B", asserted=0x09)  # \t (tab character)
            type_name_offset = class_name_reader.position
            type_name = class_name_reader.unpack_string(encoding="ascii")
            self.class_names[type_name_offset] = type_name
            self.class_hashes[type_name] = hsh
            # TODO: Hashes are checked in `TypeInfo` with everything else.

    def unpack_type_entries(
        self,
        type_section_reader: BinaryReader,
        entry_specs: list[EntrySpecStruct],
        section_end_offset: int,
    ) -> list[PackFileType]:
        """Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on write.
        """
        type_entries = []
        for i, entry_spec in enumerate(entry_specs):
            class_name = self.class_names[entry_spec.type_name_offset]

            if i < len(entry_specs) - 1:
                data_size = entry_specs[i + 1].local_data_offset - entry_spec.local_data_offset
            else:
                data_size = section_end_offset - entry_spec.local_data_offset

            type_section_reader.seek(entry_spec.local_data_offset)
            type_entry = PackFileType(class_name=class_name)
            type_entry.unpack(type_section_reader, data_size=data_size, long_varints=self.header.pointer_size == 8)
            type_entries.append(type_entry)

        return type_entries

    def unpack_item_entries(
        self,
        data_section_reader: BinaryReader,
        item_entry_specs: list[EntrySpecStruct],
        section_end_offset: int,
    ) -> list[PackFileItem]:
        """Assign `raw_data` to each packfile item.

        NOTE: Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on `pack()`.
        """
        data_entries = []
        missing_type_infos = {}  # type: dict[str, tuple[str, TypeInfo | None]]
        for i, entry_spec in enumerate(item_entry_specs):
            type_name = self.class_names[entry_spec.type_name_offset]
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

            if i < len(item_entry_specs) - 1:
                data_size = item_entry_specs[i + 1].local_data_offset - entry_spec.local_data_offset
            else:
                data_size = section_end_offset - entry_spec.local_data_offset

            data_section_reader.seek(entry_spec.local_data_offset)
            data_entry = PackFileItem(hk_type=hk_type)
            data_entry.unpack(data_section_reader, data_size=data_size, long_varints=self.header.pointer_size == 8)
            data_entries.append(data_entry)

        if missing_type_infos:
            for type_py_name, (type_name, type_info) in missing_type_infos.items():
                if type_info:
                    print(f"Type `{type_py_name}` (real name `{type_name}`) is unknown, but its type data was found:")
                    print(type_info)
                else:
                    print(f"Type `{type_py_name}` (real name `{type_name}`) is unknown and no type datas was found.")
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
        for item in self.item_entries:
            lines.append(f"    Type: {item.hk_type.__name__}")
            lines.append(
                f"        Location: ["
                f"{hex(item.local_data_offset)} - {hex(item.local_data_offset + item.item_byte_size)}"
                f"]"
            )
            lines.append(f"        Child pointers ({len(item.child_pointers)}):")
            for ref_source, ref_dest in item.child_pointers.items():
                lines.append(f"            Local Offset: {ref_source} -> {ref_dest}")
            lines.append(f"        Entry pointers ({len(item.item_pointers)}):")
            for ref_source, (dest_item, ref_dest) in item.item_pointers.items():
                lines.append(f"            Global Offset: {ref_source} -> {ref_dest} ({dest_item.hk_type.__name__})")
            lines.append(f"        Raw data length: {len(item.raw_data)}")
        return "\n".join(lines)
