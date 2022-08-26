from __future__ import annotations

__all__ = ["PackFilePacker"]

import typing as tp
from collections import deque

from soulstruct.utilities.binary import BinaryWriter

from soulstruct_havok.types.core import get_py_name, hk, Ptr_
from .structs import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.core import HKX


class PackFilePacker:

    def __init__(self, hkx: HKX):
        self.hkx = hkx

        if hkx.hk_version == "2014":
            from soulstruct_havok.types import hk2014
            self.hk_types_module = hk2014
        else:
            raise ValueError(f"Only version '2014' is supported for packfile packing, not '{hkx.hk_version}'.")

    def pack(
        self,
        header_version: PackFileVersion,
        pointer_size: int,
        is_little_endian: bool,
        padding_option: int,
        contents_version_string: bytes,
        flags: int,
        header_extension: PackFileHeaderExtension = None,
    ) -> bytes:
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
            if header_extension is None:
                raise NotImplementedError(
                    f"HKX packfile version {self.header.version} requires `packfile_header_extension`."
                )
            header_extension.default_pack(writer)
        writer.pad_align(16, b"\xFF")

        class_name_section = PackFileSectionHeader(section_tag=b"__classnames__")
        class_name_section.pack(writer)
        if self.hkx.hk_version == "2014":
            writer.pad(16, b"\xFF")
        types_section = PackFileSectionHeader(section_tag=b"__types__")
        types_section.pack(writer)
        if self.hkx.hk_version == "2014":
            writer.pad(16, b"\xFF")
        data_section = PackFileSectionHeader(section_tag=b"__data__")
        data_section.pack(writer)
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
        self.items = {}  # type: dict[hk, PackFileItemEntry]  # tracks items that have already been created
        self.packed_items = []  # type: list[PackFileItemEntry]  # items only added here once packed
        root_item = PackFileItemEntry(self.hkx.root.__class__)  # hkRootLevelContainer
        root_item.value = self.hkx.root
        self.items[self.hkx.root] = root_item

        def delayed_root_item_pack(_data_pack_queue: dict[str, deque[tp.Callable]]):
            root_item.start_writer()
            self.hkx.root.pack_packfile(root_item, self.hkx.root, self.items, _data_pack_queue, pointer_size)
            return root_item

        # This call will recursively pack all items through subqueues.
        # TODO: Will work with this for now, but it's very possible I should just use the same algorithm as tagfiles.
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
            for source_offset, (dest_item, dest_item_offset) in item.item_pointers.items():
                writer.pack(
                    "III", item.local_data_offset + source_offset, 2, dest_item.local_data_offset + dest_item_offset
                )
        writer.pad_align(16, b"\xFF")

        item_specs_offset = writer.position - data_absolute_start
        for item in self.packed_items:
            writer.pack("III", item.local_data_offset, 0, class_name_offsets[item.get_class_name()])
        writer.pad_align(16, b"\xFF")

        end_offset = writer.position - data_absolute_start
        data_section.fill(
            writer,
            absolute_data_start=data_absolute_start,
            child_pointers_offset=data_child_pointers_offset,
            item_pointers_offset=data_item_pointers_offset,
            item_specs_offset=item_specs_offset,
            exports_offset=end_offset,
            imports_offset=end_offset,
            end_offset=end_offset,
        )

        return writer.finish()

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
            item = delayed_item_pack(sub_data_pack_queue)

            # Immediately pack arrays and strings.
            while sub_data_pack_queue["array_or_string"]:
                delayed_array_or_string_pack = sub_data_pack_queue["array_or_string"].popleft()
                delayed_array_or_string_pack(sub_data_pack_queue)  # may enqueue additional "pointer" items

            item.writer.pad_align(16)  # TODO: could also align when data is packed together
            item.raw_data = item.writer.finish()
            self.packed_items.append(item)  # ordered only as they are packed, not created

            # Recur on newly collected items.
            self.process_data_pack_queue(sub_data_pack_queue["pointer"])
