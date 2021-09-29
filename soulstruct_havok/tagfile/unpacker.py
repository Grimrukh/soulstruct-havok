from __future__ import annotations

import logging
import typing as tp
from contextlib import contextmanager

from colorama import init as colorama_init, Fore
from soulstruct.utilities.binary import BinaryReader

from .structs import HKXItem
from ..enums import TagDataType, TagFormatFlags
from ..nodes import HKXNode, HKXArrayNode, HKXTupleNode
from ..types import HKXTemplate, HKXMember, HKXInterface, HKXType, HKXTypeList

if tp.TYPE_CHECKING:
    from ..core import HKX

colorama_init()


_LOGGER = logging.getLogger(__name__)

_DEBUG_HASH = False
_DEBUG_PRINT = ["XXX"]
# _DEBUG_PRINT = "Class"


class HKXTagFileUnpacker:
    
    root: tp.Optional[HKXNode]
    all_nodes: list[HKXNode]
    hkx_types: HKXTypeList
    hkx_items: list[HKXItem]
    items_in_process: list[HKXItem]  # items currently being unpacked (checked to avoid infinite recursion)
    is_compendium: bool
    compendium_ids: list[str]
    hk_version: str

    def __init__(self, reader: BinaryReader, compendium: tp.Optional[HKX] = None):
        self.root = None
        self.all_nodes = []
        self.hkx_types = HKXTypeList([])
        self.hkx_items = []
        self.items_in_process = []
        self.is_compendium = False
        self.compendium_ids = []
        self.hk_version = ""
        self.unpack(reader, compendium=compendium)

    def unpack(self, reader: BinaryReader, compendium: tp.Optional[HKX] = None):

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

                self.hkx_types = self.unpack_type_section(reader, compendium=compendium)
                self.hkx_items = self.unpack_index_section(reader, data_start_offset)

            elif root_magic == "TCM0":
                # Compendium file.
                # TODO: No hk_version SDKV section for compendium files?
                self.is_compendium = True
                with self.unpack_section(reader, "TCID") as (data_size, _):
                    self.compendium_ids = [
                        reader.unpack_string(length=8, encoding="ascii") for _ in range(data_size // 8)
                    ]

                self.hkx_types = self.unpack_type_section(reader)

        root_item = self.hkx_items[1]
        if root_item.hkx_type is None:
            raise ValueError("HKX root item had no `hkx_type`.")
        if root_item.hkx_type.name != "hkRootLevelContainer":
            raise ValueError(
                f"Unexpected HKX root item type: {root_item.hkx_type.name}. Should be 'hkRootLevelContainer'."
            )
        if root_item.node_count != 1:
            raise ValueError(f"HKX root item had a node count other than 1: {root_item.node_count}")

        # This call will recursively unpack all nodes.
        self.root = self.unpack_node(
            reader,
            hkx_type=root_item.hkx_type,
            node_offset=root_item.absolute_offset,  # first node in data
        )
        root_item.node_value = [self.root]

    def unpack_type_section(self, reader: BinaryReader, compendium: tp.Optional[HKX] = None) -> HKXTypeList:
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
                return compendium.hkx_types

            # "TYPE" HKX (does not need compendium)
            if compendium is not None:
                _LOGGER.warning("Compendium HKX was passed to TYPE-type HKX and will be ignored.")

            with self.unpack_section(reader, "TPTR"):
                pass

            with self.unpack_section(reader, "TSTR") as (tstr_size, _):
                type_names = reader.unpack_string(length=tstr_size, encoding="utf-8").split("\0")

            with self.unpack_section(reader, "TNAM", "TNA1"):
                hkx_type_count = self.unpack_var_int(reader)

                # This is where `HKXType` instances are first created, with `name` and `templates` only.
                # More data is added below in the "TBOD" section, and cross-references are resolved at the end.
                raw_hkx_types = []
                for _ in range(hkx_type_count - 1):
                    type_name = type_names[self.unpack_var_int(reader)]
                    templates = []
                    template_count = self.unpack_var_int(reader)
                    for _ in range(template_count):
                        template_name = type_names[self.unpack_var_int(reader)]
                        if template_name[0] == "t":
                            templates.append(HKXTemplate(name=template_name, type_index=self.unpack_var_int(reader)))
                        elif template_name[0] == "v":
                            templates.append(HKXTemplate(name=template_name, value=self.unpack_var_int(reader)))
                        else:
                            raise TypeError(f"Found template name that was not 't' or 'v' type: {template_name}")
                    raw_hkx_types.append(HKXType(name=type_name, templates=templates))
                hkx_types = HKXTypeList(raw_hkx_types)

            with self.unpack_section(reader, "FSTR") as (fstr_size, _):
                member_names = reader.unpack_string(length=fstr_size, encoding="utf-8").split("\0")

            with self.unpack_section(reader, "TBOD", "TBDY") as (body_section_size, _):  # doesn't matter which magic
                body_section_end = reader.position + body_section_size
                while reader.position < body_section_end:

                    hkx_type_index = self.unpack_var_int(reader)
                    hkx_parent_type_index = self.unpack_var_int(reader)
                    hkx_type_flags = self.unpack_var_int(reader)

                    if hkx_type_index == 0:
                        continue

                    hkx_type = hkx_types[hkx_type_index]
                    hkx_type.parent_type_index = hkx_parent_type_index
                    hkx_type.tag_format_flags = hkx_type_flags

                    if hkx_type.tag_format_flags & TagFormatFlags.SubType:
                        hkx_type.tag_type_flags = self.unpack_var_int(reader)

                    if (
                        hkx_type.tag_format_flags & TagFormatFlags.Pointer
                        and hkx_type.tag_type_flags & 0b0000_1111 >= 6
                    ):
                        hkx_type.pointer_type_index = self.unpack_var_int(reader)

                    if hkx_type.tag_format_flags & TagFormatFlags.Version:
                        hkx_type.version = self.unpack_var_int(reader)

                    if hkx_type.tag_format_flags & TagFormatFlags.ByteSize:
                        hkx_type.byte_size = self.unpack_var_int(reader)
                        hkx_type.alignment = self.unpack_var_int(reader)

                    if hkx_type.tag_format_flags & TagFormatFlags.AbstractValue:
                        hkx_type.abstract_value = self.unpack_var_int(reader)

                    if hkx_type.tag_format_flags & TagFormatFlags.Members:
                        member_count = self.unpack_var_int(reader)
                        hkx_type.members = [
                            HKXMember(
                                name=member_names[self.unpack_var_int(reader)],
                                flags=self.unpack_var_int(reader),
                                offset=self.unpack_var_int(reader),
                                type_index=self.unpack_var_int(reader),
                            ) for _ in range(member_count)
                        ]

                    if hkx_type.tag_format_flags & TagFormatFlags.Interfaces:
                        interface_count = self.unpack_var_int(reader)
                        hkx_type.interfaces = [
                            HKXInterface(
                                type_index=self.unpack_var_int(reader),
                                flags=self.unpack_var_int(reader)
                            )
                            for _ in range(interface_count)
                        ]

                    if hkx_type.tag_format_flags & TagFormatFlags.Unknown:
                        raise ValueError("HKX type has flag `0b1000_0000`, which is unknown and not supported.")

            with self.unpack_section(reader, "THSH"):
                hashed = []
                for _ in range(self.unpack_var_int(reader)):
                    hkx_type_index = self.unpack_var_int(reader)
                    hkx_types[hkx_type_index].hsh = reader.unpack_value("<I")
                    hashed.append(
                        (hkx_types[hkx_type_index].name, hex(reader.position),
                         hkx_type_index, hkx_types[hkx_type_index].hsh)
                    )
                if _DEBUG_HASH:
                    for h in sorted(hashed):
                        print(h[0], h[2], h[3])

            with self.unpack_section(reader, "TPAD"):
                pass

        return hkx_types

    def unpack_index_section(self, reader: BinaryReader, data_start_offset: int) -> list[HKXItem]:
        """Returns a list of `HKXItem` instances, padded at the start with `None` to preserve one-indexing."""
        items = []

        with self.unpack_section(reader, "INDX"):

            with self.unpack_section(reader, "ITEM") as (item_section_size, _):
                item_section_end = reader.position + item_section_size
                while reader.position < item_section_end:
                    item_info, relative_item_offset, node_count = reader.unpack("<III")

                    if item_info == 0:
                        # Null item.
                        items.append(None)
                        continue

                    # `item_info` combines flags (first byte) and HKX type index (last three bytes).
                    # `relative_item_offset` is relative to start of DATA section. Absolute offset is stored in item.
                    hkx_type_index = item_info & 0x00FFFFFF
                    is_ptr = bool((item_info >> 24) & 0b00010000)
                    item = HKXItem(
                        hkx_type=self.hkx_types[hkx_type_index],
                        absolute_offset=data_start_offset + relative_item_offset,
                        node_count=node_count,
                        is_ptr=is_ptr,
                        # Nodes are set during node unpack.
                    )
                    items.append(item)

            with self.unpack_section(reader, "PTCH"):
                # No patch data read here. TODO: Why?
                pass

        return items

    @contextmanager
    def unpack_section(self, reader: BinaryReader, *assert_magic) -> tuple[int, str]:
        data_size = (reader.unpack_value(">I") & 0x3FFFFFFF) - 8  # mask out 2 MSB and subtract header size
        magic = reader.unpack_string(length=4, encoding="utf-8")
        data_start_offset = reader.position
        if magic not in assert_magic:
            raise ValueError(f"Invalid tag magic: {magic}. Expected one of: {', '.join(assert_magic)}")
        try:
            yield data_size, magic
        finally:
            reader.seek(data_start_offset + data_size)

    def unpack_node(
        self, reader: BinaryReader, hkx_type: HKXType, node_offset=0, indent=0, debug_print=False
    ) -> tp.Optional[HKXNode]:
        reader.seek(node_offset)
        orig_type = hkx_type
        original_type_index = self.hkx_types.index(orig_type)
        hkx_type = hkx_type.get_base_type(self.hkx_types)

        ind = " " * indent
        debug_print = debug_print or (not _DEBUG_PRINT or hkx_type.name in _DEBUG_PRINT)
        if debug_print and hkx_type.name not in {"char", "unsigned char"}:
            print_type_name = orig_type.name if hkx_type is orig_type else f"{orig_type.name} ({hkx_type.name})"
            print(
                f"{ind}{Fore.YELLOW}Unpacking node: {print_type_name} "
                f"| {Fore.GREEN}{hkx_type.tag_data_type.name} | {Fore.CYAN}Pos: {hex(reader.position)}{Fore.RESET}"
            )

        if hkx_type.tag_data_type == TagDataType.Bool:
            value = self.unpack_bool(reader, hkx_type.tag_type_flags)
            node = HKXNode(value=value, type_index=original_type_index)

        elif hkx_type.tag_data_type == TagDataType.Int:
            value = self.unpack_int(reader, hkx_type.tag_type_flags)
            node = HKXNode(value=value, type_index=original_type_index)

        # Only 32-bit floats are unpacked properly. 16-bit floats and (yikes) 8-bit floats actually have "value" members
        # that hold their type and are treated as Class types. Note that 64-bit floats (doubles) have not been observed.
        elif hkx_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
            value = self.unpack_float(reader)
            node = HKXNode(value=value, type_index=original_type_index)

        elif hkx_type.tag_data_type == TagDataType.String:
            value = self.unpack_string(reader, indent, debug_print)
            node = HKXNode(value=value, type_index=original_type_index)

        elif hkx_type.tag_data_type == TagDataType.Pointer:
            # Pointer to a single other `HKXItem`, which may contain any number of further nodes.
            value = self.unpack_pointer(reader, indent, debug_print)
            node = HKXNode(value=value, type_index=original_type_index)

        # Floats other than 32-bit floats will be captured here as Class nodes.
        elif hkx_type.tag_data_type == TagDataType.Class or hkx_type.tag_data_type == TagDataType.Float:
            # Dictionary mapping type member names (fields, basically) to nodes.
            value = self.unpack_class(reader, hkx_type, node_offset, indent)
            node = HKXNode(value=value, type_index=original_type_index)

        elif hkx_type.tag_data_type == TagDataType.Array:
            # Array (list) of nodes, referenced with a pointer.
            value = self.unpack_array(reader, indent, debug_print)
            array_element_type = hkx_type.get_pointer_base_type(self.hkx_types)
            if (
                array_element_type.tag_data_type in {TagDataType.Bool, TagDataType.Int}
                or array_element_type.tag_type_flags == TagDataType.Float | TagDataType.Float32
            ):
                node = HKXArrayNode(value=[n.value for n in value], type_index=original_type_index)
            else:
                node = HKXNode(value=value, type_index=original_type_index)

        elif hkx_type.tag_data_type == TagDataType.Tuple:
            # Tuple of nodes, which we can fortunately distinguish from array/pointer lists easily in Python.
            value = self.unpack_tuple(reader, hkx_type, node_offset, indent)
            tuple_element_type = hkx_type.get_base_pointer_type(self.hkx_types)
            if (
                tuple_element_type.tag_data_type in {TagDataType.Bool, TagDataType.Int}
                or tuple_element_type.tag_type_flags == TagDataType.Float | TagDataType.Float32
            ):
                node = HKXTupleNode(value=tuple(n.value for n in value), type_index=original_type_index)
            else:
                node = HKXNode(value=value, type_index=original_type_index)

        else:
            raise TypeError(f"Could not unpack node from unknown HKX type: {hkx_type.name}.")

        reader.seek(node_offset + hkx_type.byte_size)

        # if debug_print and hkx_type.name not in {"char", "unsigned char"}:
        #     if isinstance(value, (bool, int, str)):
        #         print(f"{ind}{Fore.BLUE}-> value = {repr(value)}{Fore.RESET}")
        #     else:
        #         print(f"{ind}{Fore.BLUE}-> value type = {type(value)}{Fore.RESET}")

        self.all_nodes.append(node)
        return node

    def unpack_bool(self, reader: BinaryReader, tag_type_flags: int) -> bool:
        fmt = TagDataType.get_int_fmt(tag_type_flags)
        return reader.unpack_value(fmt) > 0

    def unpack_int(self, reader: BinaryReader, tag_type_flags: int) -> int:
        fmt = TagDataType.get_int_fmt(tag_type_flags)
        return reader.unpack_value(fmt)

    def unpack_float(self, reader: BinaryReader) -> float:
        return reader.unpack_value("<f")

    def unpack_string(self, reader: BinaryReader, indent: int, debug_print=False) -> str:
        string_bytearray = bytearray(
            node.value for node in self.unpack_array(reader, indent, debug_print)
        )
        return string_bytearray.decode("shift_jis_2004").rstrip("\0")

    def unpack_pointer(self, reader: BinaryReader, indent: int, debug_print=False) -> tp.Optional[HKXNode]:
        item_index = reader.unpack_value("<I")
        if item_index == 0:
            return None
        if debug_print:
            print(f"{' ' * indent}  {Fore.RED}ITEM INDEX: {item_index} ({hex(item_index)}) {Fore.RESET}")
        item = self.hkx_items[item_index]
        if item.node_value is None:
            if item in self.items_in_process:
                if item.hkx_type.tag_data_type != TagDataType.Class:
                    # I don't think this can happen, because only Class items can have any nesting (members) at all,
                    # unless an Array item somehow contains itself (unlikely).
                    raise ValueError(f"Non-Class HKX item with index {item_index} is nested within itself.")

            self.items_in_process.append(item)
            if item.hkx_type.tag_data_type == TagDataType.Class:
                # Create dictionary node now, and update its `value` later in case of member recursion.
                item.node_value = HKXNode(value={}, type_index=self.hkx_types.index(item.hkx_type))
                actual_node = self.unpack_node(
                    reader, hkx_type=item.hkx_type, node_offset=item.absolute_offset, indent=indent + 4
                )
                item.node_value.value = actual_node.value
            else:
                item.node_value = self.unpack_node(
                    reader, hkx_type=item.hkx_type, node_offset=item.absolute_offset, indent=indent + 4
                )
            self.items_in_process.remove(item)
        return item.node_value

    def unpack_class(
        self, reader: BinaryReader, hkx_type: HKXType, node_offset: int, indent: int
    ) -> dict[str, HKXNode]:
        value = {}
        for hkx_member in hkx_type.get_all_members(self.hkx_types):
            if not _DEBUG_PRINT or hkx_type.name in _DEBUG_PRINT or _DEBUG_PRINT == "Class":
                print(f"{' ' * indent}  {Fore.MAGENTA}\"{hkx_member.name}\"{Fore.RESET}")
            value[hkx_member.name] = self.unpack_node(
                reader,
                hkx_type=hkx_member.get_type(self.hkx_types),
                node_offset=node_offset + hkx_member.offset,
                indent=indent + 4,
                debug_print=not _DEBUG_PRINT or hkx_type.name in _DEBUG_PRINT or _DEBUG_PRINT == "Class",
            )
        return value

    def unpack_array(self, reader: BinaryReader, indent: int, debug_print=False) -> list[HKXNode, ...]:
        item_index = reader.unpack_value("<I")
        if item_index == 0:
            return []
        if debug_print:
            print(f"{' ' * indent}  {Fore.RED}ITEM INDEX: {item_index} ({hex(item_index)}) {Fore.RESET}")
        item = self.hkx_items[item_index]
        if item.node_value is None:
            item.node_value = [
                self.unpack_node(
                    reader,
                    hkx_type=item.hkx_type,
                    node_offset=item.absolute_offset + i * item.hkx_type.get_base_type(self.hkx_types).byte_size,
                    indent=indent + 4,
                )
                for i in range(item.node_count)
            ]
        return item.node_value

    def unpack_tuple(
        self, reader: BinaryReader, hkx_type: HKXType, node_offset: int, indent: int
    ) -> tuple[HKXNode, ...]:
        tuple_element_type = hkx_type.get_pointer_base_type(self.hkx_types)
        element_byte_size = tuple_element_type.get_base_type(self.hkx_types).byte_size
        return tuple(
            self.unpack_node(
                reader,
                hkx_type=tuple_element_type,
                node_offset=node_offset + i * element_byte_size,
                indent=indent + 4,
                debug_print=not _DEBUG_PRINT or hkx_type.name in _DEBUG_PRINT
            )
            for i in range(hkx_type.tuple_size)
        )

    @staticmethod
    def unpack_var_int(reader: BinaryReader) -> int:
        """Read a variable-sized big-endian integer from `buffer`.

        The first three bits determine the size of the integer:
            0** ->  8 bits (first 1 bit always zero, so really 7 bits)
            10* -> 16 bits (first 2 bits ignored, so really 14 bits)
            110 -> 24 bits (first 3 bits ignored, so really 21 bits)
            111 -> 32 bits (first 5 bits ignored, so really 27 bits)
        """
        byte = reader.unpack_value("B")
        if byte & 0b1000_0000:
            if byte & 0b0100_0000:
                if byte & 0b0010_0000:
                    next_byte, next_short = reader.unpack(">BH")
                    return (byte << 24 | next_byte << 16 | next_short) & 0b00000111_11111111_11111111_11111111
                else:
                    next_short = reader.unpack_value(">H")
                    return (byte << 16 | next_short) & 0b00011111_11111111_11111111
            else:
                next_byte = reader.unpack_value("B")
                return (byte << 8 | next_byte) & 0b00111111_11111111
        else:
            return byte & 0b01111111
