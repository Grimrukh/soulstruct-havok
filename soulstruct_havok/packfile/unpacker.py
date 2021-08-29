from __future__ import annotations

__all__ = ["HKXPackFileUnpacker"]

import logging
import typing as tp

from soulstruct.utilities.binary import BinaryReader
from soulstruct.utilities.inspection import get_hex_repr

from .structs import *
from ..enums import PackMemberType, TagDataType, TagFormatFlags
from ..nodes import HKXNode, HKXArrayNode, HKXTupleNode
from ..types import HKXType, HKXTypeList, HKXMember, HKXTemplate, HKXEnum

_LOGGER = logging.getLogger(__name__)

_DEBUG_PRINT = []
_DEBUG_TYPE_PRINT = False


class SectionInfo(tp.NamedTuple):
    raw_data: bytes
    child_pointers: list[dict[str, int]]
    entry_pointers: list[dict[str, int]]
    entry_specs: list[dict[str, int]]
    end_offset: int


class HKXPackFileUnpacker:

    item_entries: list[HKXItemEntry]
    hk_version: str
    root: HKXNode
    all_nodes: list[HKXNode]

    def __init__(self, reader: BinaryReader):

        self.all_nodes = []

        self.byte_order = reader.byte_order = "<" if reader.unpack_value("?", offset=0x11) else ">"
        self.header = HKXHeader(reader)

        self.hk_version = self.header.contents_version_string[3:7].decode()  # from "hk_YYYY" (e.g. "2010")

        if self.header.version.has_header_extension:
            header_extension = HKXHeaderExtension(reader)
            reader.seek(header_extension.section_offset + 0x40)
        elif reader.unpack_value("I") != 0xFFFFFFFF:
            raise ValueError(f"Expected 0xFFFFFFFF after header in `HKX` (version {hex(self.header.version)}).")

        if self.header.pointer_size not in {4, 8}:
            raise ValueError(f"HKX pointer size must be 4 or 8, not {self.header.pointer_size}.")

        class_name_info = self.unpack_section(reader)
        if class_name_info.child_pointers:
            raise AssertionError(f"Class name section has local references. Not expected!")
        if class_name_info.entry_pointers:
            raise AssertionError(f"Class name section has global references. Not expected!")
        if class_name_info.entry_specs:
            raise AssertionError(f"Class name section has data entries. Not expected!")

        type_section_info = self.unpack_section(reader)
        for type_section_entry_pointer in type_section_info.entry_pointers:
            if type_section_entry_pointer["dest_section_index"] != 1:
                raise AssertionError("type global error")

        data_section_info = self.unpack_section(reader)

        self.unpack_class_names(BinaryReader(class_name_info.raw_data))

        self.type_entries = self.unpack_type_entries(
            BinaryReader(type_section_info.raw_data),
            entry_specs=type_section_info.entry_specs,
            section_end_offset=type_section_info.end_offset
        )
        self.localize_pointers(
            self.type_entries,
            type_section_info.child_pointers,
            type_section_info.entry_pointers,
        )

        if self.type_entries:
            # Types defined inside file, minus some primitive types that are supplied manually.
            self.hkx_types = HKXTypeList(
                TypeUnpacker(self.type_entries, self.class_signatures, self.header.pointer_size).raw_hkx_types[1:]
            )
        else:
            # No types defined inside file.
            self.hkx_types = HKXTypeList.load(self.hk_version)

        self.item_entries = self.unpack_item_entries(
            BinaryReader(data_section_info.raw_data),
            entry_specs=data_section_info.entry_specs,
            section_end_offset=data_section_info.end_offset,
        )

        self.localize_pointers(
            self.item_entries,
            data_section_info.child_pointers,
            data_section_info.entry_pointers,
        )

        # from soulstruct.utilities.inspection import get_hex_repr
        # print("UNPACKER:")
        # for i, entry in enumerate(self.item_entries):
        #     print(f"DATA ENTRY {i + 1}:")
        #     print(f"HKX Type: {entry.hkx_type}")
        #     print("CHILD:", entry.child_pointers)
        #     print("ENTRY:", entry.entry_pointers)
        #     print(get_hex_repr(entry.raw_data))

        self.root = self.unpack_root_object()

    @staticmethod
    def localize_pointers(
        entries: tp.Union[list[HKXTypeEntry], list[HKXItemEntry]],
        child_pointers: list[dict[str, int]],
        entry_pointers: list[dict[str, int]],
    ):
        """Resolve pointers and attach them to their source objects."""
        for child_pointer in child_pointers:
            # Find source object and offset local to its data.
            for entry in entries:
                if (entry_source_offset := entry.get_offset_in_entry(child_pointer["source_offset"])) != -1:
                    # Check that source object is also dest object.
                    if (entry_dest_offset := entry.get_offset_in_entry(child_pointer["dest_offset"])) == -1:
                        raise AssertionError("Child pointer source object was NOT dest object. Not expected!")
                    entry.child_pointers[entry_source_offset] = entry_dest_offset
                    break
            else:
                raise ValueError(f"Could not find source/dest entry of child pointer: {child_pointer}.")

        for entry_pointer in entry_pointers:
            for entry in entries:
                if (entry_source_offset := entry.get_offset_in_entry(entry_pointer["source_offset"])) != -1:
                    source_entry = entry
                    break
            else:
                raise ValueError(f"Could not find source entry of entry pointer: {entry_pointer}.")
            for entry in entries:
                if (entry_dest_offset := entry.get_offset_in_entry(entry_pointer["dest_offset"])) != -1:
                    source_entry.entry_pointers[entry_source_offset] = (entry, entry_dest_offset)
                    break
            else:
                raise ValueError(f"Could not find dest entry of entry pointer: {entry_pointer}.")

    def unpack_section(self, reader: BinaryReader) -> SectionInfo:
        """Section structure is:

            - Packed section data (e.g. class name strings or packed entries).
            -
        """
        section = HKXSectionHeader(reader)

        if self.hk_version == "2014":
            if reader.read(16).strip(b"\xFF"):
                raise AssertionError("Expected sixteen 0xFF bytes after section header in HKX packfile version 2014.")

        absolute_data_start = section.absolute_data_start
        section_data_end = section.child_pointers_offset
        section_data = reader.unpack_bytes(length=section_data_end, offset=absolute_data_start, strip=False)
        child_pointer_count = (section.entry_pointers_offset - section.child_pointers_offset) // 8
        entry_pointer_count = (section.entry_specs_offset - section.entry_pointers_offset) // 12
        entry_spec_count = (section.exports_offset - section.entry_specs_offset) // 12

        child_pointers = []
        entry_pointers = []
        entry_specs = []

        with reader.temp_offset(offset=absolute_data_start + section.child_pointers_offset):
            for _ in range(child_pointer_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                child_pointers.append(reader.unpack_struct(CHILD_POINTER_STRUCT))
        with reader.temp_offset(offset=absolute_data_start + section.entry_pointers_offset):
            for _ in range(entry_pointer_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                entry_pointers.append(reader.unpack_struct(ENTRY_POINTER_STRUCT))
        with reader.temp_offset(offset=absolute_data_start + section.entry_specs_offset):
            for _ in range(entry_spec_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                entry_specs.append(reader.unpack_struct(ENTRY_SPEC_STRUCT))

        return SectionInfo(section_data, child_pointers, entry_pointers, entry_specs, section_data_end)

    def unpack_class_names(self, class_name_reader: BinaryReader):
        """Returns a dictionary mapping offsets (within class name section) to HKX class names and signatures."""
        self.class_names = {}
        self.class_signatures = {}

        while class_name_reader.peek_value("H") != 0xFFFF:
            signature = class_name_reader.unpack_value("I")
            class_name_reader.unpack_value("B", asserted=0x09)  # \t (tab character)
            class_name_offset = class_name_reader.position
            class_name = class_name_reader.unpack_string(encoding="ascii")
            self.class_names[class_name_offset] = class_name
            self.class_signatures[class_name] = signature

            if class_name not in CLASS_NAME_SIGNATURES:
                _LOGGER.warning(
                    f"Found unknown class name {class_name} with signature {signature}. Let Grimrukh know so this "
                    f"signature can be recorded permanently. You will not be able to pack this file until then!"
                )
            elif class_name in CLASS_NAME_SIGNATURES and CLASS_NAME_SIGNATURES[class_name] != signature:
                _LOGGER.warning(
                    f"Expected signature {CLASS_NAME_SIGNATURES[class_name]} for class name {class_name}, but found "
                    f"signature {signature}. New signature will NOT be used when packing this file."
                )

    def unpack_type_entries(
        self,
        type_section_reader: BinaryReader,
        entry_specs: list[dict[str, int]],
        section_end_offset: int,
    ) -> list[HKXTypeEntry]:
        """Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on `pack()`.
        """
        type_entries = []
        for i, entry_spec in enumerate(entry_specs):
            class_name = self.class_names[entry_spec["class_name_offset"]]

            if i < len(entry_specs) - 1:
                data_size = entry_specs[i + 1]["relative_entry_offset"] - entry_spec["relative_entry_offset"]
            else:
                data_size = section_end_offset - entry_spec["relative_entry_offset"]

            type_section_reader.seek(entry_spec["relative_entry_offset"])
            type_entry = HKXTypeEntry(class_name)
            type_entry.unpack(type_section_reader, data_size=data_size)
            type_entries.append(type_entry)

        return type_entries

    def unpack_item_entries(
        self,
        data_section_reader: BinaryReader,
        entry_specs: list[dict[str, int]],
        section_end_offset: int,
    ) -> list[HKXItemEntry]:
        """Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on `pack()`.
        """
        data_entries = []
        for i, entry_spec in enumerate(entry_specs):
            class_name = self.class_names[entry_spec["class_name_offset"]]
            hkx_type = self.hkx_types[class_name]

            if i < len(entry_specs) - 1:
                data_size = entry_specs[i + 1]["relative_entry_offset"] - entry_spec["relative_entry_offset"]
            else:
                data_size = section_end_offset - entry_spec["relative_entry_offset"]

            data_section_reader.seek(entry_spec["relative_entry_offset"])
            data_entry = HKXItemEntry(hkx_type)
            data_entry.unpack(data_section_reader, data_size=data_size)
            data_entries.append(data_entry)

        return data_entries

    def unpack_root_object(self) -> HKXNode:

        # global _DEBUG_PRINT
        # _DEBUG_PRINT = [hkx_type.name for hkx_type in self.hkx_types]

        root_hkx_type = self.hkx_types["hkRootLevelContainer"]
        root_entry = self.item_entries[0]
        if root_entry.hkx_type.name != root_hkx_type.name:
            raise TypeError(f"First data entry in HKX was not root node: {root_entry.hkx_type.name}")
        root_entry.start_reader()
        return self.unpack_node(root_entry)

    def unpack_node(
        self,
        entry: HKXItemEntry,
        type_index: int = 0,
        node_offset=0,
        indent=0,
    ) -> HKXNode:
        if node_offset != 0:
            entry.reader.seek(node_offset)
        else:
            node_offset = entry.reader.position

        original_type_index = self.hkx_types.index(entry.hkx_type) if type_index == 0 else type_index
        hkx_type = self.hkx_types[original_type_index].get_base_type(self.hkx_types)

        if entry.hkx_type.name in _DEBUG_PRINT and hkx_type.name != "unsigned char":
            print(
                f"{' ' * indent}Unpacking: {hkx_type} | {self.hkx_types[original_type_index]} "
                f"({hkx_type.tag_data_type.name}) at position {hex(entry.reader.position)}")
            # if hkx_type.tag_data_type.name == "Class":
            #     print(f"Child pointers: {entry.child_pointers}")
            #     print(f"Entry pointers: {entry.entry_pointers}")
            #     print(get_hex_repr(entry.raw_data))

        if hkx_type.tag_data_type == TagDataType.Bool:
            fmt = TagDataType.get_int_fmt(hkx_type.tag_type_flags)
            node = HKXNode(value=entry.reader.unpack_value(fmt) > 0, type_index=original_type_index)
            if entry.hkx_type.name in _DEBUG_PRINT:
                print(f"{' ' * indent}  Bool: {node.value}")

        elif hkx_type.tag_data_type == TagDataType.String:
            node = HKXNode(value=self.unpack_string_pointer(entry), type_index=original_type_index)
            if entry.hkx_type.name in _DEBUG_PRINT:
                print(f"{' ' * indent}  String: {node.value}")

        elif hkx_type.tag_data_type == TagDataType.Int:
            fmt = TagDataType.get_int_fmt(hkx_type.tag_type_flags)
            node = HKXNode(value=entry.reader.unpack_value(fmt), type_index=original_type_index)
            if entry.hkx_type.name in _DEBUG_PRINT:
                print(f"{' ' * indent}  Int: {node.value}")

        # Only 32-bit floats are unpacked properly. 16-bit floats and (yikes) 8-bit floats actually have "value" members
        # that hold their type and are treated as Class types. Note that 64-bit floats (doubles) have not been observed.
        elif hkx_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
            value = entry.reader.unpack_value("<f")
            node = HKXNode(value=value, type_index=original_type_index)
            if entry.hkx_type.name in _DEBUG_PRINT:
                print(f"{' ' * indent}  Float: {value}")

        elif hkx_type.tag_data_type == TagDataType.Pointer:
            # Pointer to another entry node (will be unpacked recursively).
            # Can also be `None`, if the pointer field is null.
            node = HKXNode(value=self.unpack_pointer(entry, indent=indent), type_index=original_type_index)

        # Floats other than 32-bit floats will be captured here as Class nodes.
        elif hkx_type.tag_data_type in {TagDataType.Class, TagDataType.Float}:
            # Dictionary mapping type member names (fields, basically) to objects.
            value = {}
            for i, hkx_member in enumerate(hkx_type.get_all_members(self.hkx_types)):
                if entry.hkx_type.name in _DEBUG_PRINT:
                    print(" " * (indent + 2) + hkx_member.name, node_offset, hkx_member.offset)
                value[hkx_member.name] = self.unpack_node(
                    entry,
                    type_index=hkx_member.type_index,
                    node_offset=node_offset + hkx_member.offset,
                    indent=indent + 4,
                )
            node = HKXNode(value=value, type_index=original_type_index)

        elif hkx_type.tag_data_type == TagDataType.Array:
            # Array (list) of objects, or a `HKXArrayNode` containing numeric/boolean primitives only.
            array_pointer_offset = entry.reader.position
            array_def_fmt = "<III" if self.header.pointer_size == 4 else "<QII"
            zero, array_size, array_capacity_and_flags = entry.reader.unpack(array_def_fmt)
            if zero != 0:
                print(zero, array_size, array_capacity_and_flags)
                raise AssertionError(f"Found non-null data at child pointer offset {array_pointer_offset}: {zero}")
            if entry.hkx_type.name in _DEBUG_PRINT:
                print(f"{' ' * indent}Array: count = {array_size}, cap/flags = {array_capacity_and_flags}")
            if array_size == 0:
                array_element_type = hkx_type.get_pointer_base_type(self.hkx_types)
                if array_element_type.tag_data_type in {TagDataType.Bool, TagDataType.Int, TagDataType.Float}:
                    node = HKXArrayNode(value=[], type_index=original_type_index)
                else:
                    node = HKXNode(value=[], type_index=original_type_index)
            else:
                try:
                    array_data_offset = entry.child_pointers[array_pointer_offset]
                except KeyError:
                    raise ValueError(
                        f"Could not find child pointer for array: {entry.hkx_type}, buffer at {entry.reader.position}"
                    )
                array_element_type = hkx_type.get_pointer_base_type(self.hkx_types)
                if (
                    array_element_type.tag_data_type in {TagDataType.Bool, TagDataType.Int}
                    or array_element_type.tag_type_flags == TagDataType.Float | TagDataType.Float32
                ):
                    with entry.reader.temp_offset(array_data_offset):
                        value = self.unpack_simple_array_node(
                            entry,
                            array_element_type.tag_data_type,
                            array_element_type.tag_type_flags & 0xFFFFFF00,
                            array_size,
                        )
                    node = HKXArrayNode(value=value, type_index=original_type_index)
                else:
                    with entry.reader.temp_offset(array_data_offset):
                        value = [
                            self.unpack_node(
                                entry,
                                type_index=hkx_type.pointer_type_index,
                                # no per-element offset needed, as array elements are tightly packed
                                indent=indent + 2,
                            ) for _ in range(array_size)
                        ]
                    node = HKXNode(value=value, type_index=original_type_index)

        elif hkx_type.tag_data_type == TagDataType.Tuple:
            # Fixed-size Tuple (`C`-style array) of objects, or a `HKXTupleNode` containing numeric/boolean primitives.
            tuple_element_type = hkx_type.get_pointer_type(self.hkx_types)
            if (
                tuple_element_type.tag_data_type in {TagDataType.Bool, TagDataType.Int}
                or tuple_element_type.tag_type_flags == TagDataType.Float | TagDataType.Float32
            ):
                value = self.unpack_simple_tuple_node(entry, tuple_element_type, hkx_type.tuple_size)
                node = HKXTupleNode(value=value, type_index=original_type_index)
            else:
                value = tuple(
                    self.unpack_node(
                        entry,
                        type_index=hkx_type.pointer_type_index,
                        node_offset=node_offset + i * hkx_type.get_pointer_base_type(self.hkx_types).byte_size,
                        indent=indent + 2
                    )
                    for i in range(hkx_type.tuple_size)
                )
                node = HKXNode(value=value, type_index=original_type_index)

        else:
            raise TypeError(f"Could not unpack object from unknown HKX type: {hkx_type.name}.")

        entry.reader.seek(node_offset + hkx_type.byte_size)
        self.all_nodes.append(node)
        return node

    def unpack_simple_array_node(
        self, entry: HKXItemEntry, element_data_type: TagDataType, element_data_variant: int, element_count: int
    ) -> list[tp.Union[bool, int, float], ...]:

        if element_data_type == TagDataType.Bool:
            fmt = TagDataType.get_int_fmt(element_data_variant)
            return [entry.reader.unpack_value(fmt) > 0 for _ in range(element_count)]
        elif element_data_type == TagDataType.Int:
            fmt = TagDataType.get_int_fmt(element_data_variant)
            return [entry.reader.unpack_value(fmt) for _ in range(element_count)]
        elif element_data_type == TagDataType.Float:
            return [entry.reader.unpack_value("<f") for _ in range(element_count)]
        raise TypeError(f"Cannot unpack simple `HKXArrayNode` from element data type: {element_data_type.name}")

    def unpack_simple_tuple_node(
        self, entry: HKXItemEntry, tuple_element_type: HKXType, tuple_size: int
    ) -> tuple[tp.Union[bool, int, float], ...]:

        element_data_type = tuple_element_type.tag_data_type
        element_data_variant = tuple_element_type.tag_type_flags & 0xFFFFFF00

        start_offset = entry.reader.position

        if element_data_type == TagDataType.Bool:
            fmt = TagDataType.get_int_fmt(element_data_variant)
            return tuple(
                entry.reader.unpack_value(fmt, offset=start_offset + i * tuple_element_type.byte_size) > 0
                for i in range(tuple_size)
            )
        elif element_data_type == TagDataType.Int:
            fmt = TagDataType.get_int_fmt(element_data_variant)
            return tuple(
                entry.reader.unpack_value(fmt, offset=start_offset + i * tuple_element_type.byte_size)
                for i in range(tuple_size)
            )
        elif element_data_type == TagDataType.Float:
            return tuple(
                entry.reader.unpack_value("<f", offset=start_offset + i * tuple_element_type.byte_size)
                for i in range(tuple_size)
            )

        raise TypeError(f"Cannot unpack simple `HKXTupleNode` from element data type: {element_data_type.name}")

    def unpack_string_pointer(self, entry: HKXItemEntry) -> tp.Optional[str]:
        """Unpack a null-terminated string (Shift-JIS) from the child pointer at the current offset.

        Rarely, no child pointer will exist (e.g. `hkaAnimationBinding["originalSkeletonName"]` in DS3). In this case,
        `None` will be returned.
        """
        pointer_offset = entry.reader.position
        entry.reader.unpack_value("<I" if self.header.pointer_size == 4 else "<Q", asserted=0)
        try:
            string_offset = entry.child_pointers[pointer_offset]
        except KeyError:
            return None
        return entry.reader.unpack_string(offset=string_offset, encoding="shift_jis_2004")

    def unpack_pointer(self, entry: HKXItemEntry, indent=0) -> tp.Optional[HKXNode]:
        source_offset = entry.reader.position
        zero = entry.reader.unpack_value("<I" if self.header.pointer_size == 4 else "<Q")
        try:
            ref_entry, ref_data_offset = entry.entry_pointers[source_offset]
        except KeyError:
            if zero != 0:
                print(entry.entry_pointers)
                raise ValueError(
                    f"Could not find entry pointer: type {entry.hkx_type}, buffer at {hex(source_offset)}."
                )
            else:
                return None
        if zero != 0:
            raise AssertionError(f"Found non-zero data at entry pointer offset: {zero}.")
        if ref_data_offset != 0:
            print(entry.entry_pointers)
            raise AssertionError(f"Data entry pointer (global ref dest) was not zero: {ref_data_offset}.")
        if ref_entry.node is not None:
            # Already instantiated. Simply return the same object.
            return ref_entry.node
        ref_entry.start_reader()
        ref_entry.node = self.unpack_node(ref_entry, indent=indent + 2)
        return ref_entry.node

    def raw_repr(self):
        lines = ["Entries:"]
        for entry in self.item_entries:
            lines.append(f"    Type: {entry.hkx_type.name}")
            lines.append(
                f"        Location: ["
                f"{hex(entry.offset_in_section)} - {hex(entry.offset_in_section + entry.entry_byte_size)}"
                f"]"
            )
            lines.append(f"        Sub pointers ({len(entry.child_pointers)}):")
            for ref_source, ref_dest in entry.child_pointers.items():
                lines.append(f"            Local Offset: {ref_source} -> {ref_dest}")
            lines.append(f"        Entry pointers ({len(entry.entry_pointers)}):")
            for ref_source, (dest_entry, ref_dest) in entry.entry_pointers.items():
                lines.append(f"            Global Offset: {ref_source} -> {ref_dest} ({dest_entry.hkx_type})")
            lines.append(f"        Raw data length: {len(entry.raw_data)}")
        return "\n".join(lines)


class TypeUnpacker:
    """Unpacks type entries and creates new array/pointer types as needed."""

    def __init__(self, type_entries: list[HKXTypeEntry], class_signatures: dict[str, int], pointer_size: int):
        self.type_entries = type_entries
        self.class_signatures = class_signatures
        self.pointer_size = pointer_size

        self.enum_dicts = {}  # type: dict[int, HKXEnum]  # maps enum entry indices to `HKXEnum` instances

        # `raw_hkx_types` is still one-indexed.
        self.raw_hkx_types = [None] * (len(self.type_entries) + 1)  # type: list[tp.Optional[HKXType]]
        primitives = HKXTypeList.load_2010().get_deferenced_primitives()
        self.raw_hkx_types.extend(primitives)
        for p in primitives:
            self.reference_primitive(p)

        self.observed_member_flags = {}

        # Tuples of classes that had not yet been defined require post-insertion of size and alignment.
        self.tuple_types = []  # type: list[HKXType]

        for entry in self.type_entries:
            if entry.class_name == "hkClass":
                entry.start_reader()
                self.unpack_class_type(entry)

        for tuple_type in self.tuple_types:
            count = tuple_type.templates[1].value
            tuple_type.byte_size = self.raw_hkx_types[tuple_type.pointer_type_index].byte_size * count
            tuple_type.alignment = next_power_of_two(tuple_type.byte_size)

        hkx_type_list = HKXTypeList(self.raw_hkx_types[1:])

        hkx_type_list.append(
            HKXType(
                name="T*",
                parent_type_index=0,
                pointer_type_index=hkx_type_list.get_type_index("hkReferencedObject"),
                byte_size=4,
                alignment=4,
                tag_format_flags=11,
                tag_type_flags=6,
                templates=[HKXTemplate(
                    name="tT",
                    type_index=hkx_type_list.get_type_index("hkReferencedObject"),
                )],
            )
        )
        ref_variant_ptr_type = len(hkx_type_list)

        hkx_type_list.append(
            HKXType(
                name="hkRefVariant",
                parent_type_index=0,
                pointer_type_index=hkx_type_list.get_type_index("hkReferencedObject"),
                byte_size=4,
                alignment=4,
                members=[HKXMember(
                    name="ptr",
                    flags=36,
                    offset=0,
                    type_index=ref_variant_ptr_type,
                )]
            )
        )

        # TODO: Use hkRefVariant below.

        if _DEBUG_TYPE_PRINT:
            print(hkx_type_list)

        # TODO: Three non-zero flags observed: 1024, 1536, and 256. 1024 is fairly common, others are very rare.
        #  1536 is used for just one member "constraintsSlave", which incidentally uses a pointer variant called
        #  "hkViewPtr". I suspect that's what it means.
        #  Meaning completely unknown.

    # noinspection PyTypeChecker,PyUnresolvedReferences
    def reference_primitive(self, p: HKXType):
        # TODO: Use NodeTypeReindexer for this, surely?

        p.parent_type_index = self.raw_hkx_types.index(p.parent_type_index) if p.parent_type_index else 0
        p.pointer_type_index = self.raw_hkx_types.index(p.pointer_type_index) if p.pointer_type_index else 0

        for t in p.templates:
            if t.name[0] == "t":
                t.type_index = self.raw_hkx_types.index(t.type_index)
        for m in p.members:
            m.type_index = self.raw_hkx_types.index(m.type_index)
        for i in p.interfaces:
            i.type_index = self.raw_hkx_types.index(i.type_index)

    def unpack_class_type(self, entry: HKXTypeEntry):

        if self.pointer_size == 4:
            class_type_header = entry.reader.unpack_struct(entry.NODE_TYPE_STRUCT_32)
        else:
            class_type_header = entry.reader.unpack_struct(entry.NODE_TYPE_STRUCT_64)
        name = entry.reader.unpack_string(offset=entry.child_pointers[0], encoding="utf-8")
        parent_type_entry, parent_type_index = self.get_referenced_entry_and_index(entry, 4)
        if _DEBUG_TYPE_PRINT:
            print(
                f"\n{self.type_entries.index(entry) + 1}: {name} "
                f"| parent = {parent_type_entry.get_type_name() if parent_type_entry else None}"
            )

        # Names of enums defined (redundantly) in the class are recorded for future byte-perfect writes. I don't think
        # it's necessary for the file to be valid, though.
        class_enums = {}  # type: dict[str, HKXEnum]
        if class_type_header["enums_count"]:
            enums_offset = entry.child_pointers[16 if self.pointer_size == 4 else 24]
            with entry.reader.temp_offset(enums_offset):
                enum_dict = self.unpack_enum_type(entry, align_before_name=False, enum_offset=enums_offset)
                if enum_dict.name in class_enums:
                    raise AssertionError(f"Enum {enum_dict.name} was defined more than once in class {name}.")
                class_enums[enum_dict.name] = enum_dict  # for member use

        members = []
        member_data_offset = entry.child_pointers.get(24 if self.pointer_size == 4 else 40)
        if member_data_offset is None and _DEBUG_TYPE_PRINT:
            print(f"NO MEMBERS for type {name}")
        if member_data_offset is not None:
            with entry.reader.temp_offset(member_data_offset):
                for _ in range(class_type_header["member_count"]):
                    member_offset = entry.reader.position
                    if self.pointer_size == 4:
                        member = entry.reader.unpack_struct(entry.NODE_TYPE_MEMBER_STRUCT_32)
                    else:
                        member = entry.reader.unpack_struct(entry.NODE_TYPE_MEMBER_STRUCT_64)
                    if _DEBUG_TYPE_PRINT:
                        print(member)
                        print(entry.child_pointers)
                        print(entry.entry_pointers)
                    member_name_offset = entry.child_pointers[member_offset]
                    member_name = entry.reader.unpack_string(offset=member_name_offset, encoding="utf-8")
                    member_data_and_pointer_type = member["member_data_and_pointer_type"]
                    try:
                        member_data_type = PackMemberType.get_data_type(member_data_and_pointer_type)
                        member_pointer_type = PackMemberType.get_pointer_type(member_data_and_pointer_type)
                    except ValueError:
                        raise ValueError(
                            f"Member {member_name} of type {name} has unknown data/pointer type: "
                            f"{member_data_and_pointer_type:016b}"
                        )
                    if _DEBUG_TYPE_PRINT:
                        print(f"  Member name: {member_name}")
                        print(f"    Member data type:    {member_data_type.name}")
                        print(f"    Member pointer type: {member_pointer_type.name}")
                        print(f"    Member flags:        {member['flags']:032b}")
                        if member["flags"]:
                            print(f"        NON-ZERO FLAGS: {member['flags']}")
                        print(f"    C Array Size:        {member['c_array_size']}")
                        # print(f"    Custom attr. ptr:    {member['custom_attributes_pointer']}")  # always zero

                    self.observed_member_flags.setdefault(member['flags'], []).append(member_name)

                    member_type_entry, member_type_index = self.get_referenced_entry_and_index(
                        entry, member_offset + self.pointer_size
                    )

                    if _DEBUG_TYPE_PRINT:
                        if member_type_entry is not None:
                            print(f"    Member class:        {member_type_index} ({member_type_entry.get_type_name()})")
                        else:
                            print(f"    Member class:        None")

                    enum_dict = None  # will only be set for enum members

                    # TODO: Don't know how to detect the small number of `hkReferencedObject` pointers that use an
                    #  `hkRefPtr` redirect rather than just a `T*` pointer type. Currently `hkaSkeleton` and
                    #  `hkLocalFrame` pointers go through `hkRefPtr`, as well as a few others that seem to always be
                    #  null so far.

                    if member_data_type == PackMemberType.hkArray:
                        member_type_index = self.get_array_member(
                            member_type_index, name, member_type_entry, member_pointer_type
                        )

                    elif member_data_type == PackMemberType.hkPlanes:
                        # TODO: Occurs in BB. Seen with `hkVector4` subtype so far... trying to interpret as Array.
                        member_type_index = self.get_array_member(
                            member_type_index, name, member_type_entry, member_pointer_type
                        )

                    elif member_data_type == PackMemberType.hkClass:
                        # `member_type_index` is already correct (no pointers).
                        if member_pointer_type != PackMemberType.void:
                            raise AssertionError(f"Found non-Void pointer type for Class member {member_name}.")

                    elif member_data_type == PackMemberType.Pointer:
                        if member_pointer_type == PackMemberType.hkClass:
                            pass  # `member_type_index` is correct
                        elif member_pointer_type == PackMemberType.void:
                            member_type_index = self.get_primitive_type_index("void")  # void pointer
                        else:
                            raise AssertionError(f"Invalid pointer type for Pointer: {member_pointer_type.name}")
                        member_type_index = self.get_pointer_member(member_type_index, name, member_type_entry)

                    elif member_data_type in {PackMemberType.hkEnum, PackMemberType.hkFlags}:
                        # TODO: `hkFlags` occurs in 2014. Not sure how it differs to `hkEnum`, or it its type should
                        #  be named differently.
                        enum_entry, enum_index = self.get_referenced_entry_and_index(
                            entry, member_offset + (8 if self.pointer_size == 4 else 16)
                        )
                        if enum_entry:
                            if _DEBUG_TYPE_PRINT:
                                print(f"ENUM REF: {enum_index}")
                        member_type_index, enum_dict = self.get_enum_member(
                            name, enum_entry, member_pointer_type, enum_index
                        )

                    else:
                        if member_pointer_type != PackMemberType.void:
                            raise AssertionError(f"Found non-Void pointer type for class member {member_name}.")
                        member_type_index = self.get_primitive_type_index(member_data_type.name)

                    # Convert to Tuple (wrap in new "T[N]" type) if needed.
                    if member["c_array_size"] > 0:
                        if _DEBUG_TYPE_PRINT:
                            print(member_type_index, self.raw_hkx_types[member_type_index])
                        member_type_index = self.create_Tuple(member_type_index, member["c_array_size"])

                    members.append(
                        HKXMember(
                            name=member_name,
                            flags=member["flags"],
                            offset=member["member_byte_offset"],
                            type_index=member_type_index,
                            hkx_enum=enum_dict,
                        )
                    )

        hkx_type = HKXType(
            name=name,
            parent_type_index=parent_type_index,
            pointer_type_index=0,  # Class types only here
            version=class_type_header["version"],
            byte_size=class_type_header["byte_size"],
            alignment=min(16, next_power_of_two(class_type_header["byte_size"])),
            # TODO: abstract_value?
            hsh=self.class_signatures.get(name, 0),  # TODO: not sure if packfile signatures == tagfile hashes
            members=members,
            tag_format_flags=TagFormatFlags.get_packfile_type_flags(has_version=False),  # all versions are zero
            tag_type_flags=TagDataType.Class,
        )

        entry_index = self.type_entries.index(entry)
        self.raw_hkx_types[entry_index + 1] = hkx_type  # replacing `None`

    def unpack_enum_type(self, entry: HKXTypeEntry, align_before_name: bool, enum_offset=0) -> HKXEnum:
        """Unpack and return a `HKXEnum` name -> value dictionary.

        These are packed on their own, as genuine `type_entries`, and are also embedded inside the class entries that
        have members that use them. The genuine ones are simply unpacked and discarded, and the indices where they
        occur are overriden with the real `hkEnum` types created when their members are encountered. The dictionary is
        loaded into the `hkx_enum` attribute of the member (only needed to regenerate the type section properly when
        writing these packfiles).
        """

        if self.pointer_size == 4:
            enum_type_struct = entry.reader.unpack_struct(entry.NODE_TYPE_ENUM_STRUCT_32)
        else:
            enum_type_struct = entry.reader.unpack_struct(entry.NODE_TYPE_ENUM_STRUCT_64)
        if align_before_name:
            entry.reader.align(16)
        name = entry.reader.unpack_string(offset=entry.child_pointers[enum_offset + 0], encoding="utf-8")
        items = []
        if _DEBUG_TYPE_PRINT:
            print(f"   Enum {name}:")
        with entry.reader.temp_offset(entry.child_pointers[enum_offset + self.pointer_size]):
            for _ in range(enum_type_struct["items_count"]):
                item_value = entry.reader.unpack_value("<I" if self.pointer_size == 4 else "<Q")
                item_name_offset = entry.child_pointers[entry.reader.position]
                item_name = entry.reader.unpack_string(offset=item_name_offset, encoding="utf-8")
                entry.reader.unpack_value("<I" if self.pointer_size == 4 else "<Q", asserted=0)
                if _DEBUG_TYPE_PRINT:
                    print(f"       {item_name} = {item_value}")
                items.append((item_name, item_value))

        return HKXEnum(name, items)

    def get_array_member(
        self,
        member_type_index: int,
        type_name: str,
        member_type_entry: HKXTypeEntry,
        pointer_type: PackMemberType,
    ) -> int:
        if pointer_type == PackMemberType.Pointer:
            array_type_index = self.get_pointer_member(member_type_index, type_name, member_type_entry)
        elif pointer_type == PackMemberType.hkClass:
            # `member_type_index` is already correct for `Class` pointer type.
            array_type_index = member_type_index
        else:
            array_type_index = self.get_primitive_type_index(pointer_type.name)

        return self.create_hkArray(array_type_index=array_type_index)

    def get_pointer_member(
        self,
        member_type_index: int,
        type_name: str,
        member_type_entry: HKXTypeEntry,
    ) -> int:
        pointer_type = "tStar"

        # TODO: Not using `hkRefVariant` at the moment.

        if member_type_entry:
            # TODO: hkRefPtr might be used to point to any object in `NamedVariants["variants"]`?
            if type_name == "hkaAnimationContainer" or member_type_entry.get_type_name() in {"hkLocalFrame"}:
                # TODO: What's special about hkaAnimationContainer and hkLocalFrame (which is always a null
                #  pointer anyway)? Why do they get a `hkRefPtr`? I think there are more of these
                #  in other HKX files, possibly...
                pointer_type = "hkRefPtr"

        if pointer_type == "tStar":
            return self.create_tStar(member_type_index)
        elif pointer_type == "hkRefVariant":
            return self.get_primitive_type_index("hkRefVariant")
        elif pointer_type == "hkRefPtr":
            return self.create_hkRefPtr(member_type_index)

    def get_enum_member(
        self,
        type_name: str,
        enum_entry: HKXTypeEntry,
        member_pointer_type: PackMemberType,
        enum_index: int,
    ) -> tuple[int, tp.Optional[dict[str, int]]]:

        if not enum_entry:
            # Null type. Observed once, for hkpShape["type"], which does not appear in any actual data.
            # Using enum parent type.
            if _DEBUG_TYPE_PRINT:
                print("NO ENUM ENTRY")
            return self.get_primitive_type_index(member_pointer_type.name), None

        enum_name = enum_entry.get_type_name()

        # TODO: Some enums have identical names: "Type", "FlagsEnum", etc.
        if enum_index in self.enum_dicts:
            # `hkEnum` type has already been created.
            if _DEBUG_TYPE_PRINT:
                print(f"EXISTING ENUM: {enum_name}")
            enum_dict = self.enum_dicts[enum_index]
            return enum_index, enum_dict

        # Unpack enum entry and create `hkEnum` type.
        enum_entry = self.type_entries[enum_index - 1]
        enum_entry.start_reader()
        enum_dict = self.unpack_enum_type(enum_entry, align_before_name=False)
        self.enum_dicts[enum_index] = enum_dict
        enum_type_index = self.create_hkEnum(
            enum_name=f"{type_name}::{enum_name}",
            pointer_type=member_pointer_type,
            enum_entry_index=enum_index,
        )
        return enum_type_index, enum_dict

    def get_referenced_entry_and_index(
        self, entry: HKXTypeEntry, pointer_offset
    ) -> tuple[tp.Optional[HKXTypeEntry], int]:
        if pointer_offset in entry.entry_pointers:
            type_entry, zero = entry.entry_pointers[pointer_offset]
            if zero != 0:
                raise AssertionError(f"Found type entry pointer placeholder other than zero: {zero}")
            # This index will also be the index of its `HKXType`, once all entries are converted.
            type_index = self.type_entries.index(type_entry) + 1
            return type_entry, type_index
        else:
            # Member is not a class or pointer.
            return None, 0

    def get_primitive_type_index(self, primitive_type_name: str) -> int:
        hits = [
            hkx_type for hkx_type in self.raw_hkx_types
            if isinstance(hkx_type, HKXType) and hkx_type.name == primitive_type_name
        ]
        if len(hits) > 1:
            raise KeyError(f"Multiple `HKXType`s with primitive name: {primitive_type_name}")
        elif not hits:
            raise KeyError(f"No `HKXType`s with primitive name: {primitive_type_name}")
        primitive_type = hits[0]
        return self.raw_hkx_types.index(primitive_type)

    def get_primitive_type_index_and_alignment(self, primitive_type_name: str) -> tuple[int, int]:
        hits = [
            hkx_type for hkx_type in self.raw_hkx_types
            if isinstance(hkx_type, HKXType) and hkx_type.name == primitive_type_name
        ]
        if len(hits) > 1:
            raise KeyError(f"Multiple `HKXType`s with primitive name: {primitive_type_name}")
        elif not hits:
            raise KeyError(f"No `HKXType`s with primitive name: {primitive_type_name}")
        primitive_hkx_type = hits[0]
        return self.raw_hkx_types.index(primitive_hkx_type), primitive_hkx_type.alignment

    def create_Tuple(self, tuple_type_index: tp.Union[HKXType, int], count: int) -> int:
        """Create a simple `T[N]` tuple type, pointing to `tuple_type_index`."""

        type_template = HKXTemplate(name="tT", type_index=tuple_type_index)
        count_template = HKXTemplate(name="vN", value=count)

        tuple_type = HKXType(
            name="T[N]",
            pointer_type_index=tuple_type_index,
            byte_size=-1,  # set after all types unpacked
            alignment=-1,  # set after all types unpacked
            tag_format_flags=TagFormatFlags.get_pointer_flags(has_members=False),
            tag_type_flags=TagDataType.Tuple | (count << 8),
            templates=[type_template, count_template],
        )

        self.tuple_types.append(tuple_type)

        self.raw_hkx_types.append(tuple_type)
        return len(self.raw_hkx_types) - 1  # latest index

    def create_hkEnum(self, enum_name: str, pointer_type: PackMemberType, enum_entry_index: int) -> int:
        """Create a simple `hkEnum` child of the given size type.

        Unlike other created types, this type directly overwrites the `enum class` that was unpacked (before this was
        called) from the file type entries.
        """

        if self.raw_hkx_types[enum_entry_index] is not None:
            raise ValueError(f"`hkEnum` {enum_name} has already been created at entry index {enum_entry_index}.")

        enum_base_type_index = self.get_primitive_type_index(pointer_type.name)
        enum_base_type = self.raw_hkx_types[enum_base_type_index]

        enum_type = HKXType(
            name=enum_name,
            byte_size=enum_base_type.byte_size,
            alignment=enum_base_type.alignment,
            tag_format_flags=TagFormatFlags.SubType | TagFormatFlags.ByteSize,
            tag_type_flags=TagDataType.from_packfile_integer(pointer_type),
        )

        self.raw_hkx_types.append(enum_type)
        enum_type_index = len(self.raw_hkx_types) - 1

        enum_template = HKXTemplate(name="tENUM", type_index=enum_type_index)
        storage_template = HKXTemplate(name="tSTORAGE", type_index=enum_base_type_index)

        hkEnum = HKXType(
            name="hkEnum",
            parent_type_index=enum_base_type_index,
            templates=[enum_template, storage_template],
            tag_format_flags=0,  # no subtype
        )

        if _DEBUG_TYPE_PRINT:
            print(f"CREATING ENUM at index {enum_entry_index}")
        self.raw_hkx_types[enum_entry_index] = hkEnum  # replaces `None`
        return enum_entry_index

    def create_hkRefPtr(self, hk_type_index: tp.Union[int, HKXType]) -> int:
        """Create a simple `hkRefPtr` type that points to the given `referenced_type` (`HKXType` or `int` index), and
        return its index.

        These pointers reference OTHER entries in the data section, unlike "T*" pointers, which reference child
        objects in the SAME entry. These still use a "T*" pointer to do the action heavy lifting, as a "ptr" member.
        """

        pointer_index = self.create_tStar(hk_type_index)
        template = HKXTemplate(name="tTYPE", type_index=hk_type_index)
        member = HKXMember(name="ptr", flags=36, offset=0, type_index=pointer_index)

        hkRefPtr = HKXType(
            name="hkRefPtr",
            pointer_type_index=hk_type_index,
            tag_format_flags=TagFormatFlags.get_pointer_flags(has_members=True),
            tag_type_flags=TagDataType.Pointer,
            templates=[template],
            members=[member],
            byte_size=self.pointer_size,
            alignment=self.pointer_size,
        )

        self.raw_hkx_types.append(hkRefPtr)
        return len(self.raw_hkx_types) - 1

    def create_tStar(self, pointer_type_index: int) -> int:
        """Create a simple "T*" pointer type that points to the given `pointer_type_index` and return its index.

        These pointers reference child objects in the SAME entry in the data section, unlike `hkRefPtr` pointers, which
        reference OTHER entries in the data section.
        """

        template = HKXTemplate(name="tT", type_index=pointer_type_index)
        tStar = HKXType(
            name="T*",
            pointer_type_index=pointer_type_index,
            tag_format_flags=TagFormatFlags.get_pointer_flags(has_members=False),
            tag_type_flags=TagDataType.Pointer,
            templates=[template],
            byte_size=self.pointer_size,
            alignment=self.pointer_size,
        )

        self.raw_hkx_types.append(tStar)
        return len(self.raw_hkx_types) - 1

    def create_hkArray(self, array_type_index: int) -> int:
        """Create `hkArray` type and its children, and return type index of new `hkArray` type.

        The only important aspect of an `hkArray` is its `array_type`, which is specified in template "tT" and is the
        same type pointed to by its `m_data` member pointer type "T*". This `array_type` is exactly what is represented
        by the `PackMemberType` in the second type byte (passed here as `member_pointer_type`).

        If `member_pointer_type` is `Pointer`, then `member_class_index` is referenced by an intermediate `hkRefPtr`
        type for both "tT" template and the `m_data` member.
        """

        type_template = HKXTemplate(
            name="tT", type_index=array_type_index
        )
        allocator_template = HKXTemplate(
            name="tAllocator", type_index=self.get_primitive_type_index("hkContainerHeapAllocator")
        )
        m_data = HKXMember(
            name="m_data", flags=34, offset=0, type_index=self.create_tStar(array_type_index)
        )
        m_size = HKXMember(
            name="m_size", flags=34, offset=4, type_index=self.get_primitive_type_index("int")
        )
        m_capacityAndFlags = HKXMember(
            name="m_capacityAndFlags", flags=34, offset=8, type_index=self.get_primitive_type_index("int")
        )

        hkArray = HKXType(
            name="hkArray",
            pointer_type_index=array_type_index,
            tag_format_flags=TagFormatFlags.get_pointer_flags(has_members=True),
            tag_type_flags=TagDataType.Array,
            byte_size=12 if self.pointer_size == 4 else 16,
            alignment=4 if self.pointer_size == 4 else 8,
            templates=[type_template, allocator_template],
            members=[m_data, m_size, m_capacityAndFlags],
        )

        self.raw_hkx_types.append(hkArray)
        return len(self.raw_hkx_types) - 1


def next_power_of_two(n) -> int:
    if n == 1:
        return 2
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    n += 1
    return n
