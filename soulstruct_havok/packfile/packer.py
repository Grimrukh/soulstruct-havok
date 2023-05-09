from __future__ import annotations

__all__ = ["PackFilePacker"]

import typing as tp
from collections import deque
from dataclasses import dataclass
from types import ModuleType

from soulstruct.utilities.binary import BinaryWriter, ByteOrder

from soulstruct_havok.types.core import get_py_name, hk, Ptr_
from .structs import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.core import HKX


@dataclass(slots=True, init=False)
class PackFilePacker:
    """Handles a single `HKX` packfile packing operation."""
    # TODO: Broken.

    hkx: HKX
    hk_types_module: ModuleType

    header: PackFileHeader
    # Tracks item entries that have already been created.
    item_entries: dict[hk, PackFileItemEntry]
    # Tracks item entries that have been packed.
    packed_items: list[PackFileItemEntry]

    def __init__(self, hkx: HKX):
        self.hkx = hkx

        if hkx.hk_version == "2010":
            from soulstruct_havok.types import hk2010
            self.hk_types_module = hk2010
        elif hkx.hk_version == "2014":
            from soulstruct_havok.types import hk2014
            self.hk_types_module = hk2014
        else:
            raise ValueError(
                f"Only versions '2010' and '2014' are currently supported for packfile packing, not '{hkx.hk_version}'."
            )

    def to_writer(self, header_info: PackfileHeaderInfo) -> BinaryWriter:
        byte_order = ByteOrder.LittleEndian if header_info.is_little_endian else ByteOrder.BigEndian
        writer = BinaryWriter(byte_order=byte_order)

        # TODO: Do the "contents" header indices/offsets vary? I don't imagine so, not for my scope anyway.
        self.header = PackFileHeader(
            version=header_info.header_version,
            pointer_size=header_info.pointer_size,
            is_little_endian=header_info.is_little_endian,
            padding_option=header_info.padding_option,
            contents_version_string=header_info.contents_version_string,
            flags=header_info.flags,
        )

        self.header.to_writer(writer)
        if self.header.version.has_header_extension:
            if header_info.header_extension is None:
                raise NotImplementedError(
                    f"HKX packfile version {self.header.version} requires `packfile_header_extension`."
                )
            header_info.header_extension.to_writer(writer)
        writer.pad_align(16, b"\xFF")

        class_name_section = PackFileSectionHeader.get_reserved_header(section_tag=b"__classnames__")
        class_name_section.to_writer(writer)
        if self.hkx.hk_version == "2014":
            writer.pad(16, b"\xFF")
        types_section = PackFileSectionHeader.get_reserved_header(section_tag=b"__types__")
        types_section.to_writer(writer)
        if self.hkx.hk_version == "2014":
            writer.pad(16, b"\xFF")
        data_section = PackFileSectionHeader.get_reserved_header(section_tag=b"__data__")
        data_section.to_writer(writer)
        if self.hkx.hk_version == "2014":
            writer.pad(16, b"\xFF")

        # CLASS SECTION

        # Start with primitive class names and root class name.
        class_names = ["hkClass", "hkClassMember", "hkClassEnum", "hkClassEnumItem", "hkRootLevelContainer"]
        self.collect_class_names(self.hkx.root, class_names)
        class_section_absolute_data_start = writer.position
        class_name_offsets = {}  # type: dict[str, int]
        for class_name in class_names:
            try:
                hsh = TYPE_NAME_HASHES[self.hkx.hk_version][class_name]
            except KeyError:
                # Get hash from Python type.
                try:
                    py_type = getattr(self.hk_types_module, get_py_name(class_name))  # type: tp.Type[hk]
                except AttributeError:
                    raise KeyError(f"Unknown Havok {self.hkx.hk_version} class: {class_name}")
                hsh = py_type.get_hsh()
                if hsh is None:
                    raise KeyError(
                        f"Hash of Havok {self.hkx.hk_version} class `{py_type.__name__}` is required for packfile "
                        f"pack, but is unknown."
                    )
            writer.pack("IB", hsh, 0x09)
            class_name_offsets[class_name] = writer.position - class_section_absolute_data_start
            writer.append(class_name.encode("ascii") + b"\0")
        writer.pad_align(16, b"\xFF")
        class_section_end_offset = writer.position - class_section_absolute_data_start
        class_name_section.fill_type_name_or_type_section(
            writer, class_section_absolute_data_start, class_section_end_offset
        )

        # TYPES SECTION  # TODO: currently always written empty
        types_section.fill_type_name_or_type_section(writer, absolute_data_start=writer.position, end_offset=0)

        # ITEM (DATA) SECTION
        data_absolute_start = writer.position
        self.item_entries = {}
        self.packed_items = []
        root_item = PackFileItemEntry(self.hkx.root.__class__, long_varints=header_info.long_varints)  # hkRootLevelContainer
        root_item.value = self.hkx.root
        self.item_entries[self.hkx.root] = root_item

        def delayed_root_item_pack(_data_pack_queue: dict[str, deque[tp.Callable]]):
            root_item.start_writer()
            self.hkx.root.pack_packfile(
                root_item, self.hkx.root, self.item_entries, _data_pack_queue
            )
            return root_item

        # This call will recursively pack all items through subqueues.
        # TODO: Will work with this for now, but it's very possible I should just use the same algorithm as tagfiles.
        with hk.set_types_dict(self.hk_types_module):
            self.process_data_pack_queue(deque([delayed_root_item_pack]))

        for item in self.packed_items:
            # Packed entry data.
            item.local_data_offset = writer.position - data_absolute_start  # offset in data section
            writer.append(item.raw_data)

        data_child_pointers_offset = writer.position - data_absolute_start
        for item in self.packed_items:
            for source_offset, dest_offset in item.child_pointers.items():
                writer.pack("II", item.local_data_offset + source_offset, item.local_data_offset + dest_offset)
        writer.pad_align(16, b"\xFF")

        data_item_pointers_offset = writer.position - data_absolute_start
        for item in self.packed_items:
            for source_offset, (dest_entry, dest_entry_offset) in item.entry_pointers.items():
                writer.pack(
                    "III", item.local_data_offset + source_offset, 2, dest_entry.local_data_offset + dest_entry_offset
                )
        writer.pad_align(16, b"\xFF")

        entry_specs_offset = writer.position - data_absolute_start
        for item in self.packed_items:
            writer.pack("III", item.local_data_offset, 0, class_name_offsets[item.get_class_name()])
        writer.pad_align(16, b"\xFF")

        end_offset = writer.position - data_absolute_start
        data_section.fill_multiple(
            writer,
            absolute_data_start=data_absolute_start,
            child_pointers_offset=data_child_pointers_offset,
            item_pointers_offset=data_item_pointers_offset,
            item_specs_offset=entry_specs_offset,
            exports_offset=end_offset,
            imports_offset=end_offset,
            end_offset=end_offset,
        )

        return writer

    def collect_class_names(self, instance: hk, class_names: list[str]) -> list[str]:
        """Collect names of all `Ptr` data types from `instance`, recursively."""
        for member in instance.members:
            member_value = getattr(instance, member.name)
            if issubclass(member.type, Ptr_):
                # Class names are NOT collected for "null pointers". Such class names (and their hashes) are not
                # included in the packfile.
                if member_value is not None:
                    member_data_class_name = type(member_value).get_real_name()
                    if member_data_class_name not in class_names:
                        class_names.append(member_data_class_name)
            if isinstance(member_value, hk):
                self.collect_class_names(member_value, class_names)
            elif isinstance(member_value, (list, tuple)):
                for v in member_value:
                    if isinstance(v, hk):
                        if issubclass(member.type.get_data_type(), Ptr_):
                            class_names.append(type(v).get_real_name())
                        self.collect_class_names(v, class_names)
        return class_names

    def process_data_pack_queue(self, item_pack_queue: deque[tp.Callable]):
        while item_pack_queue:
            sub_data_pack_queue = {"pointer": deque(), "array_or_string": deque()}
            delayed_item_pack = item_pack_queue.popleft()
            item = delayed_item_pack(sub_data_pack_queue)  # type: PackFileItemEntry

            # Immediately pack arrays and strings.
            while sub_data_pack_queue["array_or_string"]:
                delayed_array_or_string_pack = sub_data_pack_queue["array_or_string"].popleft()
                delayed_array_or_string_pack(sub_data_pack_queue)  # may enqueue additional "pointer" items

            item.writer.pad_align(16)  # TODO: could also align when data is packed together
            item.raw_data = bytes(item.writer)
            self.packed_items.append(item)  # ordered only as they are packed, not created

            # Recur on newly collected items.
            self.process_data_pack_queue(sub_data_pack_queue["pointer"])
