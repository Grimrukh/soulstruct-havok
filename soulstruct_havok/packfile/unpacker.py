from __future__ import annotations

__all__ = ["PackFileUnpacker"]

import logging
import typing as tp

from soulstruct.utilities.binary import BinaryReader

from soulstruct_havok.types.core import hk
from soulstruct_havok.types.exceptions import VersionModuleError, TypeNotDefinedError
from soulstruct_havok.types.info import TypeInfo, get_py_name
from .structs import *
from .type_unpacker import PackFileTypeUnpacker

_LOGGER = logging.getLogger(__name__)

_DEBUG_PRINT = []
_DEBUG_MSG = True
_DEBUG_TYPE_PRINT = False


def _DEBUG(*args, **kwargs):
    if _DEBUG_MSG:
        print(*args, **kwargs)


class SectionInfo(tp.NamedTuple):
    raw_data: bytes
    child_pointers: list[dict[str, int]]
    item_pointers: list[dict[str, int]]
    entry_specs: list[dict[str, int]]
    end_offset: int


class PackFileUnpacker:

    items: list[PackFileItemEntry]
    hk_version: str
    hk_types_info: list[TypeInfo]
    root: hk

    def __init__(self):
        self.hk_types_module = None
        self.byte_order = "<"
        self.hk_version = ""
        self.header = None  # type: tp.Optional[PackFileHeader]
        self.header_extension = None  # type: tp.Optional[PackFileHeaderExtension]

        self.type_entries = []  # type: list[PackFileTypeItem]
        self.hk_type_infos = []  # type: list[None | TypeInfo]
        self.class_names = {}  # type: dict[int, str]  # maps class name offsets to names
        self.class_hashes = {}  # type: dict[str, int]  # maps class names to hashes
        self.items = []  # type: list[PackFileItemEntry]

    def unpack(self, reader: BinaryReader, types_only=False):

        self.byte_order = reader.byte_order = "<" if reader.unpack_value("?", offset=0x11) else ">"
        self.header = PackFileHeader(reader)

        self.hk_version = self.header.contents_version_string[3:7].decode()  # from "hk_YYYY" (e.g. "2010")
        _LOGGER.info(f"Unpacking packfile with hk version: {self.hk_version}")

        if self.header.version.has_header_extension:
            self.header_extension = PackFileHeaderExtension(reader)
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
            if type_section_entry_pointer["dest_section_index"] != 1:
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
            self.hk_type_infos = PackFileTypeUnpacker(
                self.type_entries, self.class_hashes, self.header.pointer_size, self.hk_types_module
            ).type_infos
        else:
            self.hk_type_infos = []
            _LOGGER.info("NO type entries in packfile.")

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

        self.items = self.unpack_item_entries(
            BinaryReader(data_section_info.raw_data),
            item_entry_specs=data_section_info.entry_specs,
            section_end_offset=data_section_info.end_offset,
        )
        self.localize_pointers(
            self.items,
            data_section_info.child_pointers,
            data_section_info.item_pointers,
        )

        root_entry = self.items[0]
        if root_entry.hk_type != self.hk_types_module.hkRootLevelContainer:
            raise TypeError(f"First data entry in HKX was not root node: {root_entry.hk_type.__name__}")
        root_entry.start_reader()
        with hk.set_types_dict(self.hk_types_module):
            self.root = self.hk_types_module.hkRootLevelContainer.unpack_packfile(
                root_entry, pointer_size=self.header.pointer_size
            )

    @staticmethod
    def localize_pointers(
        items: tp.Union[list[PackFileTypeItem], list[PackFileItemEntry]],
        child_pointers: list[dict[str, int]],
        item_pointers: list[dict[str, int]],
    ):
        """Resolve pointers and attach them to their source objects."""
        for child_pointer in child_pointers:
            # Find source item and offset local to its data.
            for item in items:
                if (item_source_offset := item.get_offset_in_entry(child_pointer["source_offset"])) != -1:
                    # Check that source object is also dest object.
                    if (item_dest_offset := item.get_offset_in_entry(child_pointer["dest_offset"])) == -1:
                        raise AssertionError("Child pointer source object was NOT dest object. Not expected!")
                    item.child_pointers[item_source_offset] = item_dest_offset
                    break
            else:
                raise ValueError(f"Could not find source/dest entry of child pointer: {child_pointer}.")

        for item_pointer in item_pointers:
            for item in items:
                if (item_source_offset := item.get_offset_in_entry(item_pointer["source_offset"])) != -1:
                    source_item = item
                    break
            else:
                raise ValueError(f"Could not find source item of item pointer: {item_pointer}.")
            for item in items:
                if (item_dest_offset := item.get_offset_in_entry(item_pointer["dest_offset"])) != -1:
                    source_item.item_pointers[item_source_offset] = (item, item_dest_offset)
                    break
            else:
                raise ValueError(f"Could not find dest item of item pointer: {item_pointer}.")

    def unpack_section(self, reader: BinaryReader) -> SectionInfo:
        """Section structure is:

            - Packed section data (e.g. class name strings or packed entries).
            -
        """
        section = PackFileSectionHeader(reader)

        if self.hk_version == "2014":
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
                child_pointers.append(reader.unpack_struct(CHILD_POINTER_STRUCT))
        with reader.temp_offset(offset=absolute_data_start + section.item_pointers_offset):
            for _ in range(item_pointer_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                item_pointers.append(reader.unpack_struct(ITEM_POINTER_STRUCT))
        with reader.temp_offset(offset=absolute_data_start + section.item_specs_offset):
            for _ in range(item_spec_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                item_specs.append(reader.unpack_struct(ITEM_SPEC_STRUCT))

        return SectionInfo(section_data, child_pointers, item_pointers, item_specs, section_data_end)

    def unpack_class_names(self, class_name_data: bytes):
        """Returns a dictionary mapping offsets (within class name section) to HKX class names and signatures."""
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
        entry_specs: list[dict[str, int]],
        section_end_offset: int,
    ) -> list[PackFileTypeItem]:
        """Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on `pack()`.
        """
        type_entries = []
        for i, entry_spec in enumerate(entry_specs):
            class_name = self.class_names[entry_spec["type_name_offset"]]

            if i < len(entry_specs) - 1:
                data_size = entry_specs[i + 1]["local_data_offset"] - entry_spec["local_data_offset"]
            else:
                data_size = section_end_offset - entry_spec["local_data_offset"]

            type_section_reader.seek(entry_spec["local_data_offset"])
            type_entry = PackFileTypeItem(class_name)
            type_entry.unpack(type_section_reader, data_size=data_size)
            type_entries.append(type_entry)

        return type_entries

    def unpack_item_entries(
        self,
        data_section_reader: BinaryReader,
        item_entry_specs: list[dict[str, int]],
        section_end_offset: int,
    ) -> list[PackFileItemEntry]:
        """Assign `raw_data` to each packfile item.

        NOTE: Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on `pack()`.
        """
        data_entries = []
        for i, entry_spec in enumerate(item_entry_specs):
            type_name = self.class_names[entry_spec["type_name_offset"]]
            type_py_name = get_py_name(type_name)
            # print(f"Item: {i, type_py_name, entry_spec}")
            try:
                hk_type = getattr(self.hk_types_module, type_py_name)
            except AttributeError:
                # Missing type. Print `TypeInfo`.
                type_info_matches = [t for t in self.hk_type_infos[1:] if t.name == type_name]
                if not type_info_matches:
                    # No type info in file.
                    if type_py_name == type_name:
                        raise TypeNotDefinedError(
                            f"Type `{type_py_name}` is unknown and not defined in this file."
                            if type_py_name == type_name else
                            f"Type `{type_py_name}` (real name `{type_name}`) is unknown and not defined in this file."
                        )
                print(type_info_matches[0])
                raise TypeNotDefinedError(
                    f"Type `{type_py_name}` is unknown, but its info was found in this file."
                    if type_py_name == type_name else
                    f"Type `{type_py_name}` (real name `{type_name}`) is unknown, but its info was found in this file."
                )

            if i < len(item_entry_specs) - 1:
                data_size = item_entry_specs[i + 1]["local_data_offset"] - entry_spec["local_data_offset"]
            else:
                data_size = section_end_offset - entry_spec["local_data_offset"]

            data_section_reader.seek(entry_spec["local_data_offset"])
            data_entry = PackFileItemEntry(hk_type)
            data_entry.unpack(data_section_reader, data_size=data_size)
            data_entries.append(data_entry)

        return data_entries

    def raw_repr(self):
        lines = ["Entries:"]
        for item in self.items:
            lines.append(f"    Type: {item.hk_type.__name__}")
            lines.append(
                f"        Location: ["
                f"{hex(item.local_data_offset)} - {hex(item.local_data_offset + item.entry_byte_size)}"
                f"]"
            )
            lines.append(f"        Child pointers ({len(item.child_pointers)}):")
            for ref_source, ref_dest in item.child_pointers.items():
                lines.append(f"            Local Offset: {ref_source} -> {ref_dest}")
            lines.append(f"        Item pointers ({len(item.item_pointers)}):")
            for ref_source, (dest_item, ref_dest) in item.item_pointers.items():
                lines.append(f"            Global Offset: {ref_source} -> {ref_dest} ({dest_item.hk_type.__name__})")
            lines.append(f"        Raw data length: {len(item.raw_data)}")
        return "\n".join(lines)
