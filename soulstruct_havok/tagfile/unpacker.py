from __future__ import annotations

import logging
import typing as tp
from contextlib import contextmanager

from soulstruct.utilities.binary import BinaryReader

from soulstruct_havok.types.core import hk
from soulstruct_havok.types.exceptions import VersionModuleError, TypeNotDefinedError
from soulstruct_havok.types.info import *
from soulstruct_havok.enums import TagFormatFlags
from .structs import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.core import HKX
    from soulstruct_havok.types import hk2015

_LOGGER = logging.getLogger(__name__)

_DEBUG_TYPES = False
_DEBUG_HASH = False


def _DEBUG_TYPE_PRINT(*args, **kwargs):
    if _DEBUG_TYPES:
        print(*args, **kwargs)


class TagFileUnpacker:
    
    root: tp.Optional[hk2015.hkRootLevelContainer]  # TODO: Bit of a hack (hard-coding 2015 hierarchy).
    hk_type_infos: list[TypeInfo]
    items: list[TagFileItem]
    is_compendium: bool
    compendium_ids: list[str]
    hk_version: str

    def __init__(self):

        self.hk_types_module = None
        self.root = None
        self.hk_type_infos = []
        self.items = []
        self.is_compendium = False
        self.compendium_ids = []
        self.hk_version = ""

    def unpack(self, reader: BinaryReader, compendium: tp.Optional[HKX] = None, types_only=False):

        with self.unpack_section(reader, "TAG0", "TCM0") as (_, root_magic):

            if root_magic == "TAG0":
                # Object file.
                self.is_compendium = False
                with self.unpack_section(reader, "SDKV"):
                    self.hk_version = reader.unpack_string(length=8, encoding="utf-8")
                    if self.hk_version.startswith("2015") and not types_only:
                        from soulstruct_havok.types import hk2015
                        self.hk_types_module = hk2015
                    elif self.hk_version.startswith("2018") and not types_only:
                        from soulstruct_havok.types import hk2018
                        self.hk_types_module = hk2018
                    else:
                        raise VersionModuleError(f"No Havok type module for version: {self.hk_version}")

                with self.unpack_section(reader, "DATA"):
                    data_start_offset = reader.position
                    # Skipping over data section for now.

                self.hk_type_infos = self.unpack_type_section(reader, compendium=compendium)

                if not types_only:

                    # Attach Python classes to each non-generic `TypeInfo`.

                    missing_type_names = []
                    missing_type_py_defs = []

                    for type_info in self.hk_type_infos[1:]:
                        if type_info.name in type_info.GENERIC_TYPE_NAMES:
                            continue
                        try:
                            py_class = getattr(self.hk_types_module, type_info.py_name)  # type: tp.Type[hk]
                        except AttributeError:
                            # Missing Python definition. Create a (possibly rough) Python definition to print.
                            missing_type_names.append(type_info.name)
                            missing_type_py_defs.append(type_info.get_rough_py_def())
                        else:
                            type_info.check_py_class_match(py_class)
                            type_info.py_class = py_class

                    if missing_type_names:
                        # Types are printed in reverse order for copy-pasting to module, as member types are generally
                        # defined AFTER their owner classes in Havok files, but we need the opposite in Python.
                        for new_py_def in reversed(missing_type_py_defs):
                            print(new_py_def + "\n\n")
                        raise TypeNotDefinedError(
                            f"Unknown Havok types in file (definitions printed above): "
                            f"{list(reversed(missing_type_names))}"
                        )

                    self.items = self.unpack_index_section(reader, data_start_offset)

            elif root_magic == "TCM0":
                # Compendium file.
                # TODO: No hk_version SDKV section for compendium files?
                self.is_compendium = True
                with self.unpack_section(reader, "TCID") as (data_size, _):
                    self.compendium_ids = [
                        reader.unpack_string(length=8, encoding="ascii") for _ in range(data_size // 8)
                    ]

                self.hk_type_infos = self.unpack_type_section(reader)

        if not types_only:

            root_item = self.items[1]
            if root_item.hk_type is None:
                raise ValueError("Root item had no `hk_type`.")
            if root_item.hk_type.__name__ != "hkRootLevelContainer":
                raise ValueError(
                    f"Unexpected HKX root item type: {root_item.hk_type.__name__}. Should be `hkRootLevelContainer`."
                )
            if root_item.length != 1:
                raise ValueError(f"HKX root item has a length other than 1: {root_item.length}")

            # This call will recursively unpack all items.
            self.root = self.hk_types_module.hkRootLevelContainer.unpack(reader, root_item.absolute_offset, self.items)
            root_item.value = self.root

    def unpack_type_section(self, reader: BinaryReader, compendium: tp.Optional[HKX] = None) -> list[TypeInfo]:
        """Unpack `HKXType` instances from binary data (for TYPE files) or copy list already read from compendium
        HKX (for TCRF files).

        The fact that 2015+ HKX files tend to *have* data here (or in a compendium file) is the main difference
        separating them from 2014 files.
        """

        with self.unpack_section(reader, "TYPE", "TCRF") as (_, type_magic):

            if type_magic == "TCRF":
                # Load types from compendium and return
                if compendium is None:
                    raise ValueError("Cannot parse TCRF-type HKX without `compendium` HKX.")
                compendium_id = reader.unpack_string(length=8, encoding="utf-8")
                if compendium_id not in compendium.compendium_ids:
                    raise ValueError(f"Could not find compendium ID {repr(compendium_id)} in `compendium`.")
                return compendium.unpacker.hk_type_infos

            # "TYPE" HKX (does not need compendium)
            if compendium is not None:
                _LOGGER.warning("Compendium HKX was passed to TYPE-type HKX and will be ignored.")

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

                    _DEBUG_TYPE_PRINT(f"        --> Real name: `{file_hk_types[type_index].name}`")
                    parent_type_index = self.unpack_var_int(reader)
                    if parent_type_index > 0:
                        _DEBUG_TYPE_PRINT(
                            f"    Parent type: {parent_type_index} ({file_hk_types[parent_type_index].name})"
                        )
                    else:
                        _DEBUG_TYPE_PRINT("    Parent type: None")
                    tag_format_flags = self.unpack_var_int(reader)
                    _DEBUG_TYPE_PRINT(f"    Tag format flags: {tag_format_flags}")

                    type_info = file_hk_types[type_index]
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

            with self.unpack_section(reader, "THSH"):
                hashed = []
                for _ in range(self.unpack_var_int(reader)):
                    type_index = self.unpack_var_int(reader)
                    type_info = file_hk_types[type_index]
                    type_info.hsh = reader.unpack_value("<I")
                    hashed.append((type_info.name, hex(reader.position), type_index, type_info.hsh, type_info.py_name))
                if _DEBUG_HASH:
                    for h in sorted(hashed, key=lambda x: x[3]):
                        print(h[4], h[3])

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
                    item = TagFileItem(
                        hk_type=item_hk_type_info.py_class,
                        absolute_offset=data_start_offset + relative_item_offset,
                        length=length,
                        is_ptr=is_ptr,
                    )
                    items.append(item)

            with self.unpack_section(reader, "PTCH"):
                # Patch data contains offsets (in DATA) to item indices. It isn't needed to unpack the file, but its
                # format is checked here.
                while True:
                    try:
                        type_index, offset_count = reader.unpack("<2I")
                    except TypeError:
                        break
                    else:
                        reader.unpack(f"<{offset_count}I")

        return items

    @contextmanager
    def unpack_section(self, reader: BinaryReader, *assert_magic) -> tuple[int, str]:
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
        byte = reader.unpack_value("B")
        if byte & 0b1000_0000:
            if byte & 0b0100_0000:
                if byte & 0b0010_0000:
                    next_byte, next_short = reader.unpack(">BH")
                    value = (byte << 24 | next_byte << 16 | next_short) & 0b00000111_11111111_11111111_11111111
                    if warn_small_size and value < 0b00011111_11111111_11111111:
                        print(f"WARNING: varint {value} could have used less than 27 bits.")
                else:
                    next_short = reader.unpack_value(">H")

                    bit_21_int = (byte << 16 | next_short) & 0b00011111_11111111_11111111
                    if bit_21_int == 196609:
                        # Weird representation of 1 (first eight bits are 11000011, rest are all zeroes except the last)
                        return 1

                    value = (byte << 16 | next_short) & 0b00011111_11111111_11111111
                    if warn_small_size and value < 0b00111111_11111111:
                        print(f"WARNING: varint {value} could have used less than 21 bits.")
            else:
                next_byte = reader.unpack_value("B")
                value = (byte << 8 | next_byte) & 0b00111111_11111111
                if warn_small_size and value < 0b01111111:
                    print(f"WARNING: varint {value} could have used less than 14 bits.")
        else:
            value = byte & 0b01111111
            # No value is too small to warn about.
        return value

    @staticmethod
    def read_var_int(reader: BinaryReader, byte_count: int, mask: int):
        value = 0
        for bit_shift in range(8 * (byte_count - 1), -1, -8):
            value |= reader.unpack_value("<B") << bit_shift
        return value & mask

    @classmethod
    def unpack_var_int(cls, reader: BinaryReader) -> int:
        """First 1-5 bits of next byte indicate the size of the packed integer.

        Remaining bits after that marker in the first byte form part of the integer.
        """
        marker_byte = reader.peek_value("B")

        if marker_byte & 0b10000000 == 0:
            # Use last 7/8 bits.
            return cls.read_var_int(reader, 1, 0b01111111)

        # TODO: Special cases that have been found (in Elden Ring).
        if marker_byte == 0b11000011:
            # Use last 16/24 bits. TODO: Only observed value so far is 1, so the real bit count may be smaller.
            return cls.read_var_int(reader, 3, 0b11111111_11111111)

        marker = marker_byte >> 3  # examine first five bits

        if marker in range(0b00010000, 0b00011000):
            # Use last 14/16 bits.
            return cls.read_var_int(reader, 2, 0b00111111_11111111)

        if marker in range(0b00011000, 0b00011100):
            # Use last 21/24 bits.
            return cls.read_var_int(reader, 3, 0b00011111_11111111_11111111)

        if marker == 0b00011100:
            # Use last 27/32 bits.
            return cls.read_var_int(reader, 4, 0b00000111_11111111_11111111_11111111)

        if marker == 0b00011101:
            # Use last 35/40 bits.
            return cls.read_var_int(reader, 5, 0b00000111_11111111_11111111_11111111_11111111)

        if marker == 0b00011110:
            # Use last 59/64 bits.
            return cls.read_var_int(
                reader, 8, 0b00000111_11111111_11111111_11111111_11111111_11111111_11111111_11111111
            )

        raise ValueError(f"Unrecognized marker byte for Havok variable int: {format(marker_byte, '#010b')}")
