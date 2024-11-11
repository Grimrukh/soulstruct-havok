from __future__ import annotations

__all__ = ["PackFilePacker"]

import typing as tp
from collections import deque
from dataclasses import dataclass
from types import ModuleType

from soulstruct.utilities.binary import BinaryWriter, ByteOrder, RESERVED

from soulstruct_havok.enums import PyHavokModule
from soulstruct_havok.types.hk import hk
from soulstruct_havok.types.base import Ptr_
from soulstruct_havok.types.info import get_py_name
from .structs import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.core import HKX


@dataclass(slots=True, init=False)
class PackFilePacker:
    """Handles a single `HKX` packfile packing operation."""

    hkx: HKX
    hk_types_module: ModuleType

    # Header for packfile.
    header: PackFileHeader
    # Tracks item entries that have already been created.
    items: dict[hk, PackFileDataItem]
    # Tracks item entries that have been packed.
    packed_items: list[PackFileDataItem]

    def __init__(self, hkx: HKX):
        self.hkx = hkx

        py_havok_module = hkx.py_havok_module

        match py_havok_module:
            case PyHavokModule.hk550:
                from soulstruct_havok.types import hk550
                self.hk_types_module = hk550
            case PyHavokModule.hk2010:
                from soulstruct_havok.types import hk2010
                self.hk_types_module = hk2010
            case PyHavokModule.hk2014:
                from soulstruct_havok.types import hk2014
                self.hk_types_module = hk2014
            case _:
                raise ValueError(
                    f"Only Havok SDK versions from years '2010' and '2014' are currently supported for packfile "
                    f"packing, not '{hkx.hk_version}'."
                )

    def to_writer(self, header_info: PackfileHeaderInfo) -> BinaryWriter:
        byte_order = ByteOrder.LittleEndian if header_info.is_little_endian else ByteOrder.BigEndian
        writer = BinaryWriter(byte_order=byte_order)

        self.header = PackFileHeader(
            version=header_info.header_version,
            pointer_size=header_info.pointer_size,
            is_little_endian=header_info.is_little_endian,
            padding_option=header_info.padding_option,
            data_section_index=2,
            classnames_section_index=0,
            classnames_section_root_offset=RESERVED,
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
        has_extra_pads = self.hkx.hk_version.startswith("2014")
        if has_extra_pads:
            writer.pad(16, b"\xFF")
        types_section = PackFileSectionHeader.get_reserved_header(section_tag=b"__types__")
        types_section.to_writer(writer)
        if has_extra_pads:
            writer.pad(16, b"\xFF")
        data_section = PackFileSectionHeader.get_reserved_header(section_tag=b"__data__")
        data_section.to_writer(writer)
        if has_extra_pads:
            writer.pad(16, b"\xFF")

        # CLASSNAMES SECTION

        # Start with primitive class names and root class name.
        class_names = ["hkClass", "hkClassMember", "hkClassEnum", "hkClassEnumItem"]
        root_cls_name = self.hkx.root.get_real_name()  # obviously should be 'hkRootLevelContainer'
        class_names.append(root_cls_name)
        self.collect_class_names_from_members(self.hkx.root, class_names)
        class_section_absolute_data_start = writer.position
        class_name_offsets = {}  # type: dict[str, int]
        module_hashes = TYPE_NAME_HASHES[self.hkx.py_havok_module]

        for class_name in class_names:

            # The classnames section names don't have '::' hierarchy separators.
            packed_class_name = class_name.replace(":", "")

            try:
                hsh = module_hashes[packed_class_name]
            except KeyError:
                # Get hash from Python type.
                try:
                    py_type = getattr(self.hk_types_module, get_py_name(class_name))  # type: type[hk]
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

            if class_name == root_cls_name:
                # Header records the relative section offset of root class name (usually 'hkRootLevelContainer' @ 0x4b).
                self.header.fill(writer, "classnames_section_root_offset", class_name_offsets[class_name])

            writer.append(packed_class_name.encode("ascii") + b"\0")

        writer.pad_align(16, b"\xFF")
        class_section_end_offset = writer.position - class_section_absolute_data_start
        class_name_section.fill_type_name_or_type_section(
            writer, class_section_absolute_data_start, class_section_end_offset
        )

        # TYPES SECTION  # TODO: currently always written empty
        types_section.fill_type_name_or_type_section(writer, absolute_data_start=writer.position, end_offset=0)

        # ITEM (DATA) SECTION
        data_start_offset = writer.position
        self.items = {}
        self.packed_items = []
        root_item = PackFileDataItem(
            hk_type=self.hkx.root.__class__,
            byte_order=byte_order,
            long_varints=header_info.long_varints)
        root_item.value = self.hkx.root
        self.items[self.hkx.root] = root_item

        def delayed_root_item_pack(_item_creation_queues: PackItemCreationQueues):
            root_item.start_writer()
            self.hkx.root.pack_packfile(
                root_item, self.hkx.root, self.items, _item_creation_queues
            )
            return root_item

        # This call will recursively pack all items through subqueues. All data is written in the order it is found
        # (e.g. primitives, non-pointer `hk` instances, fixed-length array 'structs'), except for:
        #   - `hkRelArray`: a 'short jump' array format written immediately after its `hk` instance
        #   - pointer to `hk` instance: queued for new item creation, with item pointer created
        #   - array or string: written after `hk` instance, with within-item child pointer created
        #       - nested arrays/strings written immediately after parent array/string
        #       - pointers queued for new item creation along with the above
        # Effectively, arrays and strings are written 'depth first' WITHIN items, and new items are created 'depth
        # first' as we write previous items. That means that if `hk` instance `a` points to `hk` instances `b` and `c`,'
        # and `b` points to another `hk` instance `d`, then the packed item order will be `(a, b, d, c)`, since item `d`
        # was pointed to during packing of `b`.
        with hk.set_types_dict(self.hk_types_module):
            self.process_item_creation_queue(deque([delayed_root_item_pack]))

        for item in self.packed_items:
            # Packed entry data.
            item.local_data_offset = writer.position - data_start_offset  # offset in data section
            writer.append(item.raw_data)

        data_child_pointers_offset = writer.position - data_start_offset
        for item in self.packed_items:
            for source_offset, dest_offset in item.all_child_pointers.items():
                writer.pack("II", item.local_data_offset + source_offset, item.local_data_offset + dest_offset)
        writer.pad_align(16, b"\xFF")

        item_pointers_offset = writer.position - data_start_offset
        for item in self.packed_items:
            for source_offset, (dest_entry, dest_entry_offset) in item.all_item_pointers.items():
                writer.pack(
                    "III", item.local_data_offset + source_offset, 2, dest_entry.local_data_offset + dest_entry_offset
                )
        writer.pad_align(16, b"\xFF")

        item_specs_offset = writer.position - data_start_offset
        for item in self.packed_items:
            writer.pack("III", item.local_data_offset, 0, class_name_offsets[item.get_class_name()])
        writer.pad_align(16, b"\xFF")

        end_offset = writer.position - data_start_offset
        data_section.fill_multiple(
            writer,
            absolute_data_start=data_start_offset,
            child_pointers_offset=data_child_pointers_offset,
            item_pointers_offset=item_pointers_offset,
            item_specs_offset=item_specs_offset,
            exports_offset=end_offset,
            imports_offset=end_offset,
            end_offset=end_offset,
        )

        return writer

    def process_item_creation_queue(
        self,
        item_creation_queue: deque[tp.Callable[[PackItemCreationQueues], PackFileDataItem]],
    ):
        """My best attempt at emulating the item/data packing order seen in real HKX files.

        A single packfile item represents a packed binary instance of some `hk` class (usually a `hkReferencedObject`).
        However, not every `hk` instance gets its own item, as some (most) are serialized immediately within the item
        of which they are a member. Array data and string data are serialized as close to their `hk` instances as
        possible, which is why we use the `sub_data_pack_queue` below (i.e. 'depth first' array/string serialization).
        Meanwhile, any `hk` instances that are *pointed to* by the current item's `hk` instance are enqueued for
        recursive item packing AFTER all array and string data have been packed.

        All of this starts from `root.pack_packfile(root_item, root, items, _data_pack_queue)`
        """

        while item_creation_queue:
            # We collect pointers to other items and arrays/strings in the item's members.
            delayed_item_creation = item_creation_queue.popleft()
            item_pointer_queues = PackItemCreationQueues()
            item = delayed_item_creation(item_pointer_queues)

            # Immediately pack arrays and strings within the same item.
            # Note that arrays of pointers will enqueue additional item creation functions.
            while item_pointer_queues.child_pointers:
                delayed_array_or_string_pack = item_pointer_queues.child_pointers.popleft()
                item.writer.pad_align(16)
                delayed_array_or_string_pack(item_pointer_queues)

            item.writer.pad_align(16)
            item.raw_data = bytes(item.writer)
            self.packed_items.append(item)  # ordered only as they are packed, not created

            # Recur on newly collected items (including any added during array packing above).
            self.process_item_creation_queue(item_pointer_queues.item_pointers)

    def collect_class_names_from_members(self, instance: hk, class_names: list[str]) -> list[str]:
        """Collect names of all `Ptr` data types from `instance`, recursively."""
        for member in instance.members:
            member_value = getattr(instance, member.py_name)
            if issubclass(member.type, Ptr_):
                # Class names are NOT collected for "null pointers". Such class names (and their hashes) are not
                # included in the packfile; only classes that are actually instanced.
                if member_value is not None:
                    member_data_class_name = member_value.get_real_name()
                    if member_data_class_name not in class_names:
                        class_names.append(member_data_class_name)
            if isinstance(member_value, hk):
                self.collect_class_names_from_members(member_value, class_names)
            elif isinstance(member_value, (list, tuple)):
                is_ptr_sequence = issubclass(member.type.get_data_type(), Ptr_)
                for v in member_value:
                    if isinstance(v, hk):
                        if is_ptr_sequence:
                            v_type_name = v.get_real_name()
                            if v_type_name not in class_names:
                                class_names.append(v.get_real_name())
                        self.collect_class_names_from_members(v, class_names)
        return class_names
