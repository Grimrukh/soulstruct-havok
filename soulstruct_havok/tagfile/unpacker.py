from __future__ import annotations

__all__ = ["MissingCompendiumError", "TagFileUnpacker"]

import logging
import typing as tp
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

import colorama
from soulstruct.utilities.binary import *

from soulstruct_havok.types.hk import hk
from soulstruct_havok.types.exceptions import HavokTypeError, VersionModuleError, TypeNotDefinedError, TypeMatchError
from soulstruct_havok.types.info import *
from soulstruct_havok.enums import TagFormatFlags
from .structs import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.core import HKX
    from soulstruct_havok.types import hk2015, hk2018

_LOGGER = logging.getLogger("soulstruct_havok")

colorama.init()
YELLOW = colorama.Fore.YELLOW
MAGENTA = colorama.Fore.MAGENTA
RESET = colorama.Fore.RESET


_DEBUG_TYPES = False  # Type order has been confirmed as valid several times!
_DEBUG_HASH = False


def _DEBUG_TYPE_PRINT(*args, **kwargs):
    if _DEBUG_TYPES:
        print(*args, **kwargs)


class MissingCompendiumError(Exception):
    """Raised when a TCRF-type HKX file is given with no compendium HKX."""


@dataclass(slots=True)
class TagFileUnpacker:
    
    hk_types_version: str = ""
    hk_types_module: None | ModuleType = None
    root: None | hk2015.hkRootLevelContainer | hk2018.hkRootLevelContainer = None
    hk_type_infos: list[TypeInfo] = field(default_factory=list)
    items: list[TagFileItem] = field(default_factory=list)
    is_compendium: bool = False
    compendium_ids: list[bytes] = field(default_factory=list)
    hsh_overrides: dict[str, int | None] = field(default_factory=dict)
    hk_version: str = ""

    def unpack(self, reader: BinaryReader, compendium: tp.Optional[HKX] = None, types_only=False):

        with self.unpack_section(reader, "TAG0", "TCM0") as (_, root_magic):

            if root_magic == "TAG0":
                # Object file.
                self.is_compendium = False
                with self.unpack_section(reader, "SDKV"):
                    self.hk_version = reader.unpack_string(length=8, encoding="utf-8")
                    if self.hk_version.startswith("2015") and not types_only:
                        self.hk_types_version = "hk2015"
                        from soulstruct_havok.types import hk2015
                        self.hk_types_module = hk2015
                    elif self.hk_version.startswith("2018") and not types_only:
                        self.hk_types_version = "hk2018"
                        from soulstruct_havok.types import hk2018
                        self.hk_types_module = hk2018
                    else:
                        raise VersionModuleError(f"No Havok type module for version: {self.hk_version}")

                with self.unpack_section(reader, "DATA"):
                    data_start_offset = reader.position
                    # Skipping over data section for now. We just record the offset to use later.

                self.hk_type_infos = self.unpack_type_section(reader, compendium=compendium)

                if not types_only:

                    # Attach Python classes to each non-generic `TypeInfo`.

                    modules_to_create = []  # type: list[tuple[TypeInfo, str, str]]
                    clashing_modules = []  # type: list[tuple[Exception, TypeInfo, str]]

                    module_core = self.hk_types_module.core
                    module_names = list(vars(module_core))  # key names of typed `core` module

                    for type_info in self.hk_type_infos[1:]:
                        if type_info.name in type_info.GENERIC_TYPE_NAMES:
                            continue
                        try:
                            py_class = getattr(self.hk_types_module, type_info.py_name)  # type: tp.Type[hk]
                        except AttributeError:
                            # Missing Python definition. Create a (possibly rough) Python definition to print.
                            type_module_def, init_import = type_info.get_new_type_module_and_import(module_names)
                            modules_to_create.append((type_info, type_module_def, init_import))
                        else:
                            try:
                                type_info.check_py_class_match(py_class)
                            except TypeMatchError as ex:
                                type_module_def, _ = type_info.get_new_type_module_and_import(module_names)
                                clashing_modules.append((ex, type_info, type_module_def))
                            else:
                                type_info.py_class = py_class
                                full_py_name = type_info.get_full_py_name()
                                if full_py_name in self.hsh_overrides:
                                    # We do not store the hash if it matches our Python default.
                                    if py_class.get_hsh() == self.hsh_overrides[full_py_name]:
                                        self.hsh_overrides.pop(full_py_name)

                    if modules_to_create:

                        init_imports = []
                        types_path = Path(__file__).parent / f"../types/{self.hk_types_version}"

                        for type_info, type_module_def, init_import in modules_to_create:
                            new_file = types_path / f"{type_info.py_name}.py"
                            new_file.write_text(type_module_def)
                            _LOGGER.info(f"# Wrote new type file: {new_file.resolve()}")
                            init_imports.append(type_info.py_name)

                        print(f"\nImport lines to add to `types.{self.hk_types_version}.__init__.py`:")
                        for line in init_imports:
                            print(f"from .{line} import {line}")
                        # Don't raise exception until type match errors have been reported below.

                    if clashing_modules:
                        for error, type_info, type_module_def in clashing_modules:
                            _LOGGER.error(error)
                            print(f"\n# {type_info.py_name} NEW MODULE:\n\n" + type_module_def)
                        raise HavokTypeError(
                            f"{len(clashing_modules)} Havok type match errors occurred. New module strings that match "
                            f"the type info in this Havok file have been printed above."
                        )

                    if modules_to_create:
                        raise TypeNotDefinedError(
                            f"Unknown Havok types in file. New type modules created, but may need their imports "
                            f"fixed. Types:"
                            f"{[info.name for info, _, _ in modules_to_create]}"
                        )

                    self.items = self.unpack_index_section(reader, data_start_offset)

            elif root_magic == "TCM0":
                # Compendium file.
                # TODO: No hk_version SDKV section for compendium files?
                self.is_compendium = True
                with self.unpack_section(reader, "TCID") as (data_size, _):
                    self.compendium_ids = [reader.read(8) for _ in range(data_size // 8)]
                self.hk_type_infos = self.unpack_type_section(reader)
                return

        if not types_only:

            root_item = self.items[1]
            if root_item.hk_type is None:
                raise ValueError("Root item had no `hk_type`.")
            if root_item.hk_type.__name__ != "hkRootLevelContainer":
                _LOGGER.warning(
                    f"Root item of HKX file was `{root_item.hk_type.__name__}` instead of `hkRootLevelContainer`."
                )
            if root_item.length != 1:
                raise ValueError(f"HKX root item has a length other than 1: {root_item.length}")

            with hk.set_types_dict(self.hk_types_module):
                # This call will recursively unpack all items.
                self.root = root_item.hk_type.unpack_tagfile(reader, root_item.absolute_offset, self.items)
            root_item.value = self.root

    def unpack_type_section(self, reader: BinaryReader, compendium: tp.Optional[HKX] = None) -> list[TypeInfo]:
        """Unpack `HKXType` instances from binary data (for TYPE files) or copy list already read from compendium
        HKX (for TCRF files).

        The fact that 2015+ HKX files tend to *have* data here (or in a compendium file) is the main difference
        separating them from 2014 files.
        """

        with self.unpack_section(reader, "TYPE", "TCRF") as (_, type_magic):

            if type_magic == "TCRF":
                # Load types from compendium and return.
                if compendium is None:
                    raise MissingCompendiumError("Cannot parse TCRF-type HKX without `compendium` HKX.")
                compendium_id = reader.read(8)
                if compendium_id not in compendium.compendium_ids:
                    raise ValueError(f"Could not find compendium ID {repr(compendium_id)} in `compendium`.")
                return compendium.unpacker.hk_type_infos

            # "TYPE" HKX (does not need compendium)
            if compendium is not None:
                _LOGGER.warning("Compendium HKX was passed to TYPE-type HKX and will be ignored.")

            if self.peek_section(reader, "TPTR"):
                with self.unpack_section(reader, "TPTR"):
                    pass

            with self.unpack_section(reader, "TSTR") as (tstr_size, _):
                type_names = reader.unpack_string(length=tstr_size, encoding="utf-8").split("\0")

            with self.unpack_section(reader, "TNAM", "TNA1"):
                file_type_count = self.unpack_var_int(reader)

                # This is where `TagTypeInfo` instances are first created, with `name` and `templates` only.
                # More data is added below in the "TBOD" section, and cross-references are resolved at the end.
                # Note that we don't look for the Python class until the body is defined, so we can present more
                # detailed information in the event that we can't find a type and have to raise an exception.
                file_hk_types = [None]  # padded to preserve one-indexing
                for _ in range(file_type_count - 1):
                    type_name_index = self.unpack_var_int(reader)
                    template_count = self.unpack_var_int(reader)
                    type_name = type_names[type_name_index]
                    type_info = TypeInfo(name=type_name)
                    type_info.templates = []
                    for _ in range(template_count):
                        template_name_index = self.unpack_var_int(reader)
                        template_name = type_names[template_name_index]
                        template_value = self.unpack_var_int(reader)  # could be a type index ('t') or value ('v')
                        type_info.templates.append(TemplateInfo(template_name, template_value))
                    file_hk_types.append(type_info)

                # Assign template types.
                for type_info in file_hk_types[1:]:
                    for template in type_info.templates:
                        if template.is_type:
                            template.type_info = file_hk_types[template.value]

            with self.unpack_section(reader, "FSTR") as (fstr_size, _):
                member_names = reader.unpack_string(length=fstr_size, encoding="utf-8").split("\0")

            with self.unpack_section(reader, "TBOD", "TBDY") as (body_section_size, _):  # doesn't matter which magic
                body_section_end = reader.position + body_section_size
                while reader.position < body_section_end:

                    _DEBUG_TYPE_PRINT("TYPE:")
                    type_index = self.unpack_var_int(reader)
                    _DEBUG_TYPE_PRINT(f"    Type index: {type_index}")

                    if type_index == 0:
                        continue  # null type
                    type_info = file_hk_types[type_index]

                    _DEBUG_TYPE_PRINT(f"        --> Real name: `{type_info.name}`")
                    parent_type_index = self.unpack_var_int(reader)
                    if parent_type_index > 0:
                        _DEBUG_TYPE_PRINT(
                            f"    Parent type: {parent_type_index} ({file_hk_types[parent_type_index].name})"
                        )
                    else:
                        _DEBUG_TYPE_PRINT("    Parent type: None")
                    tag_format_flags = self.unpack_var_int(reader)
                    _DEBUG_TYPE_PRINT(f"    Tag format flags: {tag_format_flags}")

                    if parent_type_index > 0:
                        type_info.parent_type_info = file_hk_types[parent_type_index]
                    type_info.tag_format_flags = tag_format_flags

                    if tag_format_flags & TagFormatFlags.SubType:
                        type_info.tag_type_flags = tag_type_flags = self.unpack_var_int(reader)
                        _DEBUG_TYPE_PRINT(f"    Tag type flags: {tag_type_flags}")

                    if tag_format_flags & TagFormatFlags.Pointer and tag_type_flags & 0b0000_1111 >= 6:
                        type_info.pointer_type_index = self.unpack_var_int(reader)
                        if type_info.pointer_type_index > 0:
                            _DEBUG_TYPE_PRINT(
                                f"    Pointer type: {type_info.pointer_type_index} "
                                f"({file_hk_types[type_info.pointer_type_index].name})"
                            )
                        else:
                            _DEBUG_TYPE_PRINT("    Pointer type: None")
                        type_info.pointer_type_info = file_hk_types[type_info.pointer_type_index]

                    if tag_format_flags & TagFormatFlags.Version:
                        type_info.version = self.unpack_var_int(reader)
                        _DEBUG_TYPE_PRINT(f"    Version: {type_info.version}")

                    if tag_format_flags & TagFormatFlags.ByteSize:
                        type_info.byte_size = self.unpack_var_int(reader)
                        _DEBUG_TYPE_PRINT(f"    Byte size: {type_info.byte_size}")
                        type_info.alignment = self.unpack_var_int(reader)
                        _DEBUG_TYPE_PRINT(f"    Alignment: {type_info.alignment}")

                    if tag_format_flags & TagFormatFlags.AbstractValue:
                        type_info.abstract_value = self.unpack_var_int(reader)
                        _DEBUG_TYPE_PRINT(f"    Abstract value: {type_info.abstract_value}")

                    if tag_format_flags & TagFormatFlags.Members:
                        type_info.members = []
                        member_count = self.unpack_var_int(reader)
                        _DEBUG_TYPE_PRINT(f"    Member count: {member_count}")
                        for _ in range(member_count):
                            member_name_index = self.unpack_var_int(reader)
                            member_name = member_names[member_name_index]
                            _DEBUG_TYPE_PRINT(f"      Member name index: {member_name_index} ({member_name})")
                            member_flags = self.unpack_var_int(reader)
                            _DEBUG_TYPE_PRINT(f"        Flags: {member_flags}")
                            if member_flags < 32:
                                raise ValueError(f"Member flags were less than 32, which isn't possible.")
                            member_offset = self.unpack_var_int(reader)
                            _DEBUG_TYPE_PRINT(f"        Offset: {member_offset}")
                            member_type_index = self.unpack_var_int(reader)
                            member_type_info = file_hk_types[member_type_index]
                            _DEBUG_TYPE_PRINT(f"        Type index: {member_type_index} ({member_type_info.name})")
                            type_info.members.append(
                                MemberInfo(
                                    name=member_name,
                                    flags=member_flags,
                                    offset=member_offset,
                                    type_index=member_type_index,
                                    type_info=file_hk_types[member_type_index],
                                )
                            )

                    if tag_format_flags & TagFormatFlags.Interfaces:
                        interface_count = self.unpack_var_int(reader)
                        _DEBUG_TYPE_PRINT(f"Interface count: {interface_count}")
                        type_info.interfaces = [
                            InterfaceInfo(
                                type_index=(interface_type_index := self.unpack_var_int(reader)),
                                flags=self.unpack_var_int(reader),
                                type_info=file_hk_types[interface_type_index],
                            )
                            for _ in range(interface_count)
                        ]

                    if tag_format_flags & TagFormatFlags.Unknown:
                        raise ValueError(
                            f"Havok type '{type_info.name}' has flag `0b1000_0000`, which is unknown and not supported."
                        )

                if _DEBUG_TYPES:
                    lines = []
                    for i, hk_type in enumerate(file_hk_types[1:]):
                        line = f"{i + 1}: {hk_type.py_name}"
                        while hk_type.pointer_type_info:
                            hk_type = hk_type.pointer_type_info
                            line += f"[{hk_type.py_name}]"
                        lines.append(line)
                    types = "\n    ".join(lines)
                    print(f"{YELLOW}Final unpacked type list:\n    {types}{RESET}")

            if self.peek_section(reader, "THSH"):
                unhashed_types = file_hk_types[1:]
                with self.unpack_section(reader, "THSH"):
                    hashed = []
                    if _DEBUG_HASH:
                        print(f"{MAGENTA}Unpacked hashes:{RESET}")
                    for _ in range(self.unpack_var_int(reader)):
                        type_index = self.unpack_var_int(reader)
                        type_info = file_hk_types[type_index]
                        full_py_name = type_info.get_full_py_name()
                        self.hsh_overrides[full_py_name] = type_info.hsh = reader.unpack_value("<I")
                        if _DEBUG_HASH:
                            print(f"    {MAGENTA}`{full_py_name}`: {type_info.hsh}{RESET}")
                        hashed.append((type_info.hsh, full_py_name))
                        unhashed_types.remove(type_info)
                    if _DEBUG_HASH:
                        print(f"{MAGENTA}Unpacked hashes (sorted):{RESET}")
                        for type_hsh, type_name in sorted(hashed):
                            print(f"    {MAGENTA}`{type_name}`: {type_hsh}{RESET}")
                for type_info in unhashed_types:
                    # Types that did not explicitly get a hash receive `None` override.
                    # Types that DID get a hash, but it was the expected hash, will be removed from the overrides.
                    self.hsh_overrides[type_info.get_full_py_name()] = None

            if self.peek_section(reader, "THSH"):
                with self.unpack_section(reader, "TPAD"):
                    pass

        # Assign member types.
        for t in file_hk_types[1:]:
            for m in t.members:
                m.deindexify(file_hk_types)

        return file_hk_types

    def unpack_index_section(self, reader: BinaryReader, data_start_offset: int) -> list[TagFileItem]:
        """Returns a list of `TagFileItem` instances, padded at the start with `None` to preserve one-indexing (which
        corresponds to a null item in the actual file)."""
        items = []

        with self.unpack_section(reader, "INDX"):

            with self.unpack_section(reader, "ITEM") as (item_section_size, _):
                item_section_end = reader.position + item_section_size
                while reader.position < item_section_end:
                    item_info, relative_item_offset, length = reader.unpack("<III")

                    if item_info == 0:
                        # Null item.
                        items.append(None)
                        continue

                    # `item_info` combines flags (first byte) and HK type index (last three bytes).
                    # `relative_item_offset` is relative to start of DATA section. Absolute offset is stored in item.
                    type_index = item_info & 0x00FFFFFF
                    is_ptr = bool((item_info >> 24) & 0b00010000)
                    item_hk_type_info = self.hk_type_infos[type_index]
                    # print(f"Unpacking item {len(items)}: type index {type_index} ({item_hk_type_info.name})")
                    item = TagFileItem(
                        hk_type=item_hk_type_info.py_class,
                        absolute_offset=data_start_offset + relative_item_offset,
                        length=length,
                        is_ptr=is_ptr,
                    )
                    items.append(item)

            # with self.unpack_section(reader, "PTCH"):
            #     # Patch data contains offsets (in DATA) to item indices. It isn't needed to unpack the file, but its
            #     # format is checked here.
            #     while True:
            #         try:
            #             type_index, offset_count = reader.unpack("<2I")
            #         except TypeError:
            #             break
            #         else:
            #             reader.unpack(f"<{offset_count}I")

        return items

    @staticmethod
    def peek_section(reader: BinaryReader, *assert_magic) -> bool:
        """Looks ahead to see if an optional section is present."""
        try:
            with reader.temp_offset(reader.position):
                # Mask out 2 most significant bits and subtract this header size.
                _ = (reader.unpack_value(">I") & 0x3FFFFFFF) - 8  # data_size
                magic = reader.unpack_string(length=4, encoding="utf-8")
        except reader.ReaderError:
            return False
        if magic not in assert_magic:
            return False
        return True

    @staticmethod
    @contextmanager
    def unpack_section(reader: BinaryReader, *assert_magic) -> tuple[int, str]:
        # Mask out 2 most significant bits and subtract header size.
        data_size = (reader.unpack_value(">I") & 0x3FFFFFFF) - 8
        magic = reader.unpack_string(length=4, encoding="utf-8")
        data_start_offset = reader.position
        if magic not in assert_magic:
            raise ValueError(f"Invalid tag magic: {magic}. Expected one of: {', '.join(assert_magic)}")
        try:
            yield data_size, magic
        finally:
            reader.seek(data_start_offset + data_size)

    @staticmethod
    def unpack_var_int_old(reader: BinaryReader, warn_small_size=False) -> int:
        """Read a variable-sized big-endian integer from `buffer`.

        The first three bits determine the size of the integer:
            0** ->  8 bits (first 1 bit always zero, so really 7 bits)
            10* -> 16 bits (first 2 bits ignored, so really 14 bits)
            110 -> 24 bits (first 3 bits ignored, so really 21 bits)
            111 -> 32 bits (first 5 bits ignored, so really 27 bits)

        If `warn_small_size=True`, a warning will be printed (for debugging purposes) if the number is unpacked could
        have fit in a smaller varint. This helps for detecting obstacles in the way of byte-perfect writes.
        """
        b = reader.unpack_value("B")
        if b & 0b1000_0000:
            if b & 0b0100_0000:
                if b & 0b0010_0000:
                    next_byte, next_short = reader.unpack(">BH")
                    value = (b << 24 | next_byte << 16 | next_short) & 0b00000111_11111111_11111111_11111111
                    if warn_small_size and value < 0b00011111_11111111_11111111:
                        print(f"WARNING: varint {value} could have used less than 27 bits.")
                else:
                    next_short = reader.unpack_value(">H")

                    bit_21_int = (b << 16 | next_short) & 0b00011111_11111111_11111111
                    if bit_21_int == 196609:
                        # Weird representation of 1 (first eight bits are 11000011, rest are all zeroes except the last)
                        return 1

                    value = (b << 16 | next_short) & 0b00011111_11111111_11111111
                    if warn_small_size and value < 0b00111111_11111111:
                        print(f"WARNING: varint {value} could have used less than 21 bits.")
            else:
                next_byte = reader.unpack_value("B")
                value = (b << 8 | next_byte) & 0b00111111_11111111
                if warn_small_size and value < 0b01111111:
                    print(f"WARNING: varint {value} could have used less than 14 bits.")
        else:
            value = b & 0b01111111
            # No value is too small to warn about.
        return value

    @classmethod
    def unpack_var_int(cls, reader: BinaryReader) -> int:
        """First 1-5 bits of next byte indicate the size of the packed unsigned integer.

        Remaining bits after that marker in the first byte form part of the integer.
        """
        byte_1 = reader.unpack("<B")[0]

        if byte_1 & 0b10000000 == 0:
            # Use last 7/8 bits.
            return byte_1 & 0b01111111

        # TODO: Special cases that have been found (in Elden Ring).
        if byte_1 == 0b11000011:
            # Use last 16/24 bits. TODO: Only observed value so far is 1, so the real bit count may be smaller.
            bytes_2_3 = reader.unpack("<2B")
            return (bytes_2_3[0] << 8) | bytes_2_3[1]

        marker = byte_1 >> 3  # examine first five bits (a varying number of them may be used)

        if 0b00010000 <= marker < 0b00011000:
            # Use last 14/16 bits.
            byte_2 = reader.unpack("<B")[0]
            return 0b00111111_11111111 & ((byte_1 << 8) | byte_2)

        if 0b00011000 <= marker < 0b00011100:
            # Use last 21/24 bits.
            bytes_2_3 = reader.unpack("<2B")
            return 0b00011111_11111111_11111111 & ((byte_1 << 16) | (bytes_2_3[0] << 8) | bytes_2_3[1])

        if marker == 0b00011100:
            # Use last 27/32 bits.
            reader.seek(-1, 1)
            return reader.unpack("<I")[0] & 0b00000111_11111111_11111111_11111111

        if marker == 0b00011101:
            # Use last 35/40 bits.
            bytes_2_3_4_5 = reader.unpack("<4B")
            return 0b00000111_11111111_11111111_11111111_11111111 & (
                (byte_1 << 32) | (bytes_2_3_4_5[0] << 24) | (bytes_2_3_4_5[1] << 16)
                | (bytes_2_3_4_5[2] << 8) | bytes_2_3_4_5[3]
            )

        if marker == 0b00011110:
            # Use last 59/64 bits.
            reader.seek(-1, 1)
            return reader.unpack("<Q")[0] & 0b00000111_11111111_11111111_11111111_11111111_11111111_11111111_11111111

        raise ValueError(f"Unrecognized marker byte for Havok variable int: {format(byte_1, '#010b')}")
