from __future__ import annotations

import logging
import typing as tp
from contextlib import contextmanager

from soulstruct.utilities.binary import BinaryReader

from soulstruct_havok.types.core import hk
from soulstruct_havok.types.info import *
from soulstruct_havok.enums import TagFormatFlags
from .structs import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.core import HKX
    from soulstruct_havok.types import hk2015

_LOGGER = logging.getLogger(__name__)

_DEBUG_TYPES = False
_DEBUG_HASH = False


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
        self.all_nodes = []
        self.hk_type_infos = []
        self.items = []
        self.is_compendium = False
        self.compendium_ids = []
        self.hk_version = ""

    def unpack(self, reader: BinaryReader, compendium: tp.Optional[HKX] = None, types_only=False):

        if not types_only:
            from soulstruct_havok.types import hk2015
            self.hk_types_module = hk2015

        with self.unpack_section(reader, "TAG0", "TCM0") as (_, root_magic):

            if root_magic == "TAG0":
                # Object file.
                self.is_compendium = False
                with self.unpack_section(reader, "SDKV"):
                    self.hk_version = reader.unpack_string(length=8, encoding="utf-8")
                    if self.hk_version not in {"20150100", "20160100", "20160200"}:
                        raise ValueError(f"Unsupported HKX tagfile version: {self.hk_version}.")

                with self.unpack_section(reader, "DATA"):
                    data_start_offset = reader.position
                    # Skipping over data section for now.

                self.hk_type_infos = self.unpack_type_section(reader, compendium=compendium)

                if not types_only:

                    # Attach Python classes to each non-generic `TypeInfo`.
                    for type_info in self.hk_type_infos[1:]:
                        if type_info.name in type_info.GENERIC_TYPE_NAMES:
                            continue
                        try:
                            py_class = getattr(self.hk_types_module, type_info.py_name)  # type: tp.Type[hk]
                            type_info.check_py_class_match(py_class)
                            type_info.py_class = py_class
                        except AttributeError:
                            # TODO: Create?
                            raise TypeError(f"No Python type '{type_info.py_name}'. Info:\n{self}")

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

                    type_index = self.unpack_var_int(reader)
                    parent_type_index = self.unpack_var_int(reader)
                    tag_format_flags = self.unpack_var_int(reader)

                    if type_index == 0:
                        continue  # null type

                    type_info = file_hk_types[type_index]
                    if parent_type_index > 0:
                        type_info.parent_type_info = file_hk_types[parent_type_index]
                    type_info.tag_format_flags = tag_format_flags

                    if tag_format_flags & TagFormatFlags.SubType:
                        type_info.tag_type_flags = tag_type_flags = self.unpack_var_int(reader)

                    if tag_format_flags & TagFormatFlags.Pointer and tag_type_flags & 0b0000_1111 >= 6:
                        type_info.pointer_type_index = self.unpack_var_int(reader)
                        type_info.pointer_type_info = file_hk_types[type_info.pointer_type_index]

                    if tag_format_flags & TagFormatFlags.Version:
                        type_info.version = self.unpack_var_int(reader)

                    if tag_format_flags & TagFormatFlags.ByteSize:
                        type_info.byte_size = self.unpack_var_int(reader)
                        type_info.alignment = self.unpack_var_int(reader)

                    if tag_format_flags & TagFormatFlags.AbstractValue:
                        type_info.abstract_value = self.unpack_var_int(reader)

                    if tag_format_flags & TagFormatFlags.Members:
                        member_count = self.unpack_var_int(reader)
                        type_info.members = [
                            MemberInfo(
                                name=member_names[self.unpack_var_int(reader)],
                                flags=self.unpack_var_int(reader),
                                offset=self.unpack_var_int(reader),
                                type_index=(member_type_index := self.unpack_var_int(reader)),
                                type_info=file_hk_types[member_type_index],
                            ) for _ in range(member_count)
                        ]

                    if tag_format_flags & TagFormatFlags.Interfaces:
                        interface_count = self.unpack_var_int(reader)
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
    def unpack_var_int(reader: BinaryReader, warn_small_size=False) -> int:
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
