from __future__ import annotations

__all__ = ["PackFilePacker"]

import typing as tp
from collections import deque

from soulstruct.utilities.binary import BinaryWriter

from .structs import *
from ..enums import TagDataType
from ..nodes import HKXNode
from ..types import HKXType

if tp.TYPE_CHECKING:
    from ..core import HKX

_DEBUG_PACK_PRINT = []


class PackFilePacker:

    class EntryQueue(deque[tuple[HKXNode, PackFileItemEntry]]):
        """Each instance holds `(node, entry)` pairs, where `node` is the root `HKXNode` of the given `entry` and will
        be recursively packed into it."""

    class PointerQueue(deque[tuple[int, tp.Union[str, list[HKXNode]]]]):
        """Each instance holds `(source_offset, string/array)` pairs that have yet to be written. They are unloaded
        when the calling Class node is finished packing."""

    def __init__(self, hkx: HKX):
        self.hkx = hkx
        self.hkx_types = self.hkx.hkx_types

    def pack(
        self,
        header_version=PackFileVersion.Version0x08,  # Dark Souls PTDE version
        pointer_size=4,
        is_little_endian=True,
        padding_option=0,
        contents_version_string=b"hk_2010.2.0-r1",  # Dark Souls PTDE version
        flags=0,
    ) -> bytes:
        raise NotImplementedError("Packfile packer is currently broken.")

        writer = BinaryWriter(big_endian=not is_little_endian)

        # TODO: Do the "contents" header indices/offsets vary? I don't imagine so, not for my scope anyway.
        self.header = PackFileHeader(
            version=header_version,
            pointer_size=pointer_size,
            is_little_endian=is_little_endian,
            padding_option=padding_option,
            contents_version_string=contents_version_string,
            flags=flags,
        )

        self.header.default_pack(writer)
        if self.header.version.has_header_extension:
            # TODO: Need to know default header extension values, if there are such.
            raise NotImplementedError(
                f"Cannot yet pack HKX packfile version {self.header.version} (has header extension)."
            )
        writer.pad_align(16, b"\xFF")

        class_name_section = PackFileSectionHeader(section_tag=b"__classnames__")
        class_name_section.pack(writer)
        types_section = PackFileSectionHeader(section_tag=b"__types__")
        types_section.pack(writer)
        data_section = PackFileSectionHeader(section_tag=b"__data__")
        data_section.pack(writer)

        # Class section.

        # Get all class names.
        class_names = ["hkClass", "hkClassMember", "hkClassEnum", "hkClassEnumItem", "hkRootLevelContainer"]
        self.collect_class_names(self.hkx.root, class_names=class_names)
        class_section_absolute_data_start = writer.position
        class_name_offsets = {}  # type: dict[str, int]
        for class_name in class_names:
            try:
                signature = TYPE_NAME_HASHES[self.hk_version][class_name]
            except KeyError:
                raise KeyError(
                    f"Soulstruct does not know the HKX packfile signature for class {class_name}. Please tell "
                    f"Grimrukkh and provide a native HKX packfile that contains the class, if possible."
                )
            writer.pack("IB", signature, 0x09)
            class_name_offsets[class_name] = writer.position - class_section_absolute_data_start
            writer.append(class_name.encode("ascii") + b"\0")
        writer.pad_align(16, b"\xFF")
        class_section_end_offset = writer.position - class_section_absolute_data_start
        class_name_section.fill_type_name_or_type_section(
            writer, class_section_absolute_data_start, class_section_end_offset
        )

        types_section.fill_type_name_or_type_section(writer, absolute_data_start=writer.position, end_offset=0)

        data_absolute_start = writer.position
        self.data_entries = {}  # type: dict[HKXNode, PackFileItemEntry]  # tracks entries that have already been created
        self.ordered_data_entries = []  # type: list[PackFileItemEntry]  # entries only added here after they are packed
        root_data_entry = PackFileItemEntry(self.hkx.root.get_type(self.hkx_types))  # hkRootLevelContainer
        self.data_entries[self.hkx.root] = root_data_entry
        top_level_entry_queue = self.EntryQueue([(self.hkx.root, root_data_entry)])
        self.pack_queued_entries(entry_queue=top_level_entry_queue)

        # print("PACKER:")
        # for entry in self.ordered_data_entries:
        #     from soulstruct.utilities.inspection import get_hex_repr
        #     print(entry.hkx_type)
        #     print(get_hex_repr(entry.raw_data))

        for entry in self.ordered_data_entries:
            # Packed entry data.
            entry.local_offset = writer.position - data_absolute_start  # offset in data section
            writer.append(entry.raw_data)

        data_child_pointers_offset = writer.position - data_absolute_start
        for entry in self.ordered_data_entries:
            for source_offset, dest_offset in entry.child_pointers.items():
                writer.pack("II", entry.local_offset + source_offset, entry.local_offset + dest_offset)
        writer.pad_align(16, b"\xFF")

        data_entry_pointer_offset = writer.position - data_absolute_start
        for entry in self.ordered_data_entries:
            for source_offset, (dest_entry, dest_entry_offset) in entry.entry_pointers.items():
                writer.pack(
                    "III", entry.local_offset + source_offset, 2, dest_entry.offset_in_section + dest_entry_offset
                )
        writer.pad_align(16, b"\xFF")

        data_entry_specs_offset = writer.position - data_absolute_start
        for entry in self.ordered_data_entries:
            # Entry specs.
            writer.pack("III", entry.local_offset, 0, class_name_offsets[entry.hkx_type.name])
        writer.pad_align(16, b"\xFF")

        end_offset = writer.position - data_absolute_start
        data_section.fill(
            writer,
            absolute_data_start=data_absolute_start,
            child_pointers_offset=data_child_pointers_offset,
            entry_pointers_offset=data_entry_pointer_offset,
            entry_specs_offset=data_entry_specs_offset,
            exports_offset=end_offset,
            imports_offset=end_offset,
            end_offset=end_offset,
        )

        return writer.finish()

    def collect_class_names(self, node: HKXNode, class_names: list[str]):
        if node.get_base_type(self.hkx_types).tag_data_type == TagDataType.Pointer:
            class_name = node.value.get_type_name(self.hkx_types)
            if class_name not in class_names:
                class_names.append(class_name)

        if isinstance(node.value, dict):
            for child_node in node.value.values():
                self.collect_class_names(child_node, class_names)
        elif isinstance(node.value, (tuple, list)):
            for child_node in node.value:
                self.collect_class_names(child_node, class_names)
        elif isinstance(node.value, HKXNode):
            self.collect_class_names(node.value, class_names)

    def pack_queued_entries(self, entry_queue: EntryQueue):
        while entry_queue:
            node, entry = entry_queue.popleft()
            entry.writer = BinaryWriter()  # TODO: can this be big endian?
            sub_entry_queue = self.EntryQueue()
            top_pointer_queue = self.PointerQueue()
            self.pack_node(node, entry, entry_queue=sub_entry_queue, pointer_queue=top_pointer_queue)
            self.pack_queued_data(entry, entry_queue=sub_entry_queue, pointer_queue=top_pointer_queue, indent=0)
            self.ordered_data_entries.append(entry)
            entry.writer.pad_align(16)  # TODO: could also align when data is packed together
            entry.raw_data = entry.writer.finish()
            self.pack_queued_entries(sub_entry_queue)

    def pack_node(
        self,
        node: HKXNode,
        entry: PackFileItemEntry,
        entry_queue: EntryQueue,
        pointer_queue: PointerQueue,
        hkx_type: HKXType = None,
        flag_array=False,
        indent=0,
    ):

        original_hkx_type = node.get_type(self.hkx_types) if hkx_type is None else hkx_type
        hkx_type = original_hkx_type.get_base_type(self.hkx_types)

        if entry.hkx_type.name in _DEBUG_PACK_PRINT:
            print(
                f"{' ' * indent}Packing: {hkx_type} | {original_hkx_type} "
                f"({TagDataType(hkx_type.tag_data_type).name}) at position {entry.writer.position}")

        if hkx_type.tag_data_type == TagDataType.Bool:
            fmt = TagDataType.get_int_fmt(hkx_type.tag_type_flags)
            entry.writer.pack(fmt, node.value)
            if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                print(f"{' ' * indent}  Bool: {node.value}")

        elif hkx_type.tag_data_type == TagDataType.String:
            self.pack_string(entry, pointer_queue=pointer_queue, string=node.value)
            if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                print(f"{' ' * indent}  String: {node.value}")

        elif hkx_type.tag_data_type == TagDataType.Int:
            fmt = TagDataType.get_int_fmt(hkx_type.tag_type_flags)
            entry.writer.pack(fmt, node.value)
            if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                print(f"{' ' * indent}  Int: {node.value}")

        elif hkx_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
            entry.writer.pack("<f", node.value)
            if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                print(f"{' ' * indent}  Float: {node.value}")

        elif hkx_type.tag_data_type == TagDataType.Pointer:
            self.pack_pointer(entry_node=node.value, entry=entry, entry_queue=entry_queue)

        elif hkx_type.tag_data_type == TagDataType.Class:
            # Dictionary mapping type member names (fields, basically) to nodes.
            # Iterates over `all_members`, rather than just the node dictionary, to ensure all members are present.
            class_start_offset = entry.writer.position
            if hkx_type.get_type_hierarchy(self.hkx_types)[0].name == "hkBaseObject":
                # Pointer here for the mysterious base object member.
                entry.writer.pad(self.header.pointer_size)
            for hkx_member in hkx_type.get_all_members(self.hkx_types):
                if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                    print(" " * (indent + 2) + hkx_member.name, hkx_member.offset)

                member_type = hkx_member.get_type(self.hkx_types)

                flag_array = hkx_member.name != "partitions"  # TODO: HACK! Document properly.

                # Align to relative member offset.
                entry.writer.pad(class_start_offset + hkx_member.offset - entry.writer.position)

                self.pack_node(
                    node=node.value[hkx_member.name],
                    entry=entry,
                    entry_queue=entry_queue,
                    pointer_queue=pointer_queue,
                    hkx_type=member_type,
                    flag_array=flag_array,
                    indent=indent + 4,
                )
                if member_type.alignment > 0:
                    entry.writer.pad_align(member_type.alignment)

        elif hkx_type.tag_data_type == TagDataType.Array:
            self.pack_array(array_node=node, entry=entry, pointer_queue=pointer_queue, with_flag=flag_array)

        elif hkx_type.tag_data_type == TagDataType.Struct:
            # Tuple of nodes of type `node.pointer`, which are all packed immediately (unlike arrays and their pointer
            # structs).
            for child_node in node.value:
                self.pack_node(
                    child_node,
                    entry,
                    entry_queue=entry_queue,
                    pointer_queue=pointer_queue,
                    indent=indent + 2,
                )
        else:
            raise TypeError(f"Could not pack object with unknown HKX type: {hkx_type.name}.")

        if entry.hkx_type.name in _DEBUG_PACK_PRINT:
            print(f"Aligning {hkx_type.name} at {entry.writer.position} to {hkx_type.alignment}")
        entry.writer.pad_align(hkx_type.alignment)

    def pack_string(self, entry: PackFileItemEntry, pointer_queue: PointerQueue, string: str):
        """Queue the given string to be packed, after the current array, class, or raw object is finished (whichever
        comes first)."""
        pointer_queue.append((entry.writer.position, string))
        entry.writer.pad(self.header.pointer_size)

    def pack_pointer(self, entry_node: HKXNode, entry: PackFileItemEntry, entry_queue: EntryQueue):
        if entry_node in self.data_entries:
            # Data entry for node already created (in a previous call of this method).
            deferenced_entry = self.data_entries[entry_node]
        else:
            # Create new data entry.
            deferenced_entry = PackFileItemEntry(entry_node.get_type(self.hkx_types))
            self.data_entries[entry_node] = deferenced_entry
            entry_queue.append((entry_node, deferenced_entry))
        entry.entry_pointers[entry.writer.position] = (deferenced_entry, 0)
        entry.writer.pad(self.header.pointer_size)

    def pack_array(
        self,
        array_node: HKXNode,
        entry: PackFileItemEntry,
        pointer_queue: PointerQueue,
        with_flag=True,
    ):
        """Array structs (offset, count, and capacity/flags) are packed here immediately.

        The array data itself is buffered, to be flushed when the preceding Class, Array, or Tuple has finished.
        """
        array_ptr_offset = entry.writer.position
        entry.writer.pad(self.header.pointer_size)
        entry.writer.pack("<I", len(array_node.value))
        # TODO: only found one array that doesn't use the flag (hkaBone["partitions"]).
        # Capacity is same as length, and highest bit is enabled (flags "do not free memory", I believe).
        entry.writer.pack("<I", len(array_node.value) | (1 << 31 if with_flag else 0))  # highest bit on

        if array_node.value:  # non-empty
            if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                array_element_type = array_node.get_base_type(self.hkx_types).get_pointer_type(self.hkx_types)
                print(f"Queuing array: {array_ptr_offset}, {array_element_type.name}, {len(array_node.value)}")
            pointer_queue.append((array_ptr_offset, array_node.value))

    def pack_queued_data(self, entry: PackFileItemEntry, entry_queue: EntryQueue, pointer_queue: PointerQueue, indent: int):
        """Write all queued string/array data at the current offset.

        Called when a Class, Array, or Tuple node has finished packing.
        """
        while pointer_queue:
            array_pointer_offset, string_or_array_nodes = pointer_queue.popleft()
            if isinstance(string_or_array_nodes, list):
                # List of array element nodes.
                if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                    print(f"Pre-aligning before array at {entry.writer.position}: 16")
                entry.writer.pad_align(16)  # pre-align
                entry.child_pointers[array_pointer_offset] = entry.writer.position
                if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                    print(f"Packing queued array with length {len(string_or_array_nodes)} at {entry.writer.position}")
                array_subqueue = self.PointerQueue()
                for element_node in string_or_array_nodes:
                    if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                        print(f"Packing queued {element_node.hkx_type} at node at {entry.writer.position}")
                    self.pack_node(
                        node=element_node,
                        entry=entry,
                        entry_queue=entry_queue,
                        pointer_queue=array_subqueue,
                        indent=indent + 2,
                    )
                self.pack_queued_data(entry, entry_queue=entry_queue, pointer_queue=array_subqueue, indent=indent)
            elif isinstance(string_or_array_nodes, str):
                # String. No pre-alignment needed.
                if entry.hkx_type.name in _DEBUG_PACK_PRINT:
                    print(f"Packing queued string {string_or_array_nodes} at {entry.writer.position}")
                entry.child_pointers[array_pointer_offset] = entry.writer.position
                entry.writer.append(string_or_array_nodes.encode("shift_jis_2004") + b"\0")
                entry.writer.pad_align(16)
