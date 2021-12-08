from __future__ import annotations

import typing as tp
from collections import deque
from contextlib import contextmanager

from soulstruct.utilities.binary import BinaryWriter

from soulstruct_havok.enums import TagFormatFlags
from soulstruct_havok.types.core import hk, hkArray_
from soulstruct_havok.types.info import TypeInfo
from .structs import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.core import HKX


_DEBUG_SECTIONS = False
_DEBUG_HASH = False
_DEBUG_PRINT = True


class UniqueInstance:
    """Simple hashable container that wraps item instances to make them unique for later `TagFileItem` lookup."""

    def __init__(self, value: hk | str | list):
        self.value = value


class TagFilePacker:
    """Builds "tagfile" style Havok (e.g., for Dark Souls Remastered)."""

    class ItemInstanceQueue(deque[tuple[tp.Type[hk], hk | str | list]]):
        """Holds a deque of pairs of `hk` types and their associated instance values (`hk` instances, strings or lists)
        that are to be packed into items.

        The offset of the instance's item in the "DATA" section is reserved and filled later when the queue is
        processed and the `TagFileItem` created.
        """

    type_info_dict: dict[str, TypeInfo]
    items: list[None | TagFileItem]

    def __init__(self, hkx: HKX):

        from soulstruct_havok.types import hk2015
        self.hk_types_module = hk2015

        self.hkx = hkx
        self.hk_types = list[tp.Type[hk]]
        self.items = [None]  # type: list[None | TagFileItem]  # first entry is always `None` for 1-indexing
        self.type_info_dict = {}
        self._patches = {}  # type: dict[str, list[int]]  # maps base type names to absolute item offsets using them

    def get_py_type(self, type_name: str) -> tp.Type[hk]:
        return getattr(self.hk_types_module, type_name)

    def build_type_info_dict(self):
        """Collects all types used by this file, then removes duplicate types and adds generic types as needed."""

        # Collect all types, not including generic types.
        collected_types = [
            type(self.hkx.root),
            getattr(self.hk_types_module, "hkContainerHeapAllocator"),
        ]
        collected_types += self.hkx.root.collect_types_with_instance()
        self.hk_types = []
        for hk_type in collected_types:  # remove duplicate types
            if hk_type not in self.hk_types:
                self.hk_types.append(hk_type)

        # This dictionary's order will determine ultimate indexing.
        self.type_info_dict = {}  # type: dict[str, TypeInfo]
        for hk_type in self.hk_types:
            new_types = hk_type.update_type_info_dict(self.type_info_dict)

        type_py_names = [""] + list(self.type_info_dict.keys())

        for type_info in self.type_info_dict.values():
            type_info.indexify(type_py_names)

    def pack(self) -> bytes:
        """Pack a tagfile using the `hkRootLevelContainer` (`hkx.root`).

        First, we scan the full structure and collect types to write into the tagfile's TYPE section. During this, we
        also keep track of array and pointer types for re-use (though not sure exactly how unique these end up being,
        and it's probably only good for efficiency).

        TODO: This entire class is byte-perfect except for the ordering of hashes. They seem to be ordered in a
         similar way to how items are ordered (arrays/pointers before strings, level by level) but I can't quite
         figure it out and it's barely worth it, of course.
        """

        self.build_type_info_dict()

        # self.hkx_types.convert_types_to_2015()  # TODO

        writer = BinaryWriter(big_endian=False)  # TODO: always false?

        with self.pack_section(writer, "TAG0", flag=False):

            with self.pack_section(writer, "SDKV"):
                writer.append(b"20150100")  # TODO: Always this version?

            with self.pack_section(writer, "DATA"):

                root_item = TagFileItem(hk_type=self.hkx.root.__class__, is_ptr=True, length=1)
                root_item_writer = BinaryWriter()
                self.items = [None, root_item]
                existing_items = {}
                self.hkx.root.pack(root_item_writer, self.hkx.root, self.items, existing_items)
                root_item.data = root_item_writer.finish()

                # Join item data together and record offsets.
                data_start_offset = writer.position
                for item in self.items[1:]:
                    if issubclass(item.hk_type, hkArray_):
                        writer.pad_align(16)
                    else:
                        writer.pad_align(max(2, item.hk_type.alignment))
                    base_type_name = item.hk_type.get_type_hierarchy()[0].__name__
                    self._patches.setdefault(base_type_name, []).append(writer.position)
                    item.absolute_offset = writer.position
                    writer.append(item.data)

                writer.pad_align(16)

            self.pack_type_section(writer)
            self.pack_index_section(writer, data_start_offset)

        return writer.finish()

    @contextmanager
    def pack_section(self, writer: BinaryWriter, magic: str, flag=True):

        section_start = writer.position
        if _DEBUG_SECTIONS:
            print(f"Section {magic} start: {hex(writer.position)}")

        section_start_offset = writer.position
        writer.reserve(f"{magic}_size", ">I")
        writer.append(magic[:4].encode("utf-8"))
        try:
            yield
        finally:
            writer.pad_align(4)
            section_size = (writer.position - section_start_offset) | (0x40_00_00_00 if flag else 0x0)
            writer.fill(f"{magic}_size", section_size)

            if _DEBUG_SECTIONS:
                print(f"  Section {magic} end: {hex(writer.position)} ({hex(writer.position - section_start)})")

    def pack_type_section(self, writer: BinaryWriter):

        with self.pack_section(writer, "TYPE", flag=False):

            with self.pack_section(writer, "TPTR"):
                # This pointer section is simply not used.
                writer.pad(8 * (len(self.type_info_dict) + 1))

            type_names = []
            member_names = []
            for type_info in self.type_info_dict.values():
                if type_info.name not in type_names:
                    type_names.append(type_info.name)

                for template in type_info.templates:
                    if template.name not in type_names:
                        type_names.append(template.name)

                for member in type_info.members:
                    if member.name not in member_names:
                        member_names.append(member.name)

            with self.pack_section(writer, "TSTR"):
                writer.append(("\0".join(type_names) + "\0").encode("utf-8"))

            with self.pack_section(writer, "TNAM"):
                self.pack_var_int(writer, len(self.type_info_dict) + 1)
                for type_info in self.type_info_dict.values():
                    self.pack_var_int(writer, type_names.index(type_info.name))
                    self.pack_var_int(writer, len(type_info.templates))
                    for template in type_info.templates:
                        self.pack_var_int(writer, type_names.index(template.name))
                        self.pack_var_int(writer, template.value)

            with self.pack_section(writer, "FSTR"):
                writer.append(("\0".join(member_names) + "\0").encode("utf-8"))

            with self.pack_section(writer, "TBOD"):
                # "Type body" section, where everything about a type other than its name and templates is defined.
                for i, type_info in enumerate(self.type_info_dict.values()):

                    self.pack_var_int(writer, i + 1)
                    self.pack_var_int(writer, type_info.parent_type_index)
                    self.pack_var_int(writer, type_info.tag_format_flags)

                    if type_info.tag_format_flags & TagFormatFlags.SubType:
                        self.pack_var_int(writer, type_info.tag_type_flags)

                    if type_info.tag_format_flags & TagFormatFlags.Pointer:
                        self.pack_var_int(writer, type_info.pointer_type_index)

                    if type_info.tag_format_flags & TagFormatFlags.Version:
                        self.pack_var_int(writer, type_info.version)

                    if type_info.tag_format_flags & TagFormatFlags.ByteSize:
                        self.pack_var_int(writer, type_info.byte_size)
                        self.pack_var_int(writer, type_info.alignment)

                    if type_info.tag_format_flags & TagFormatFlags.AbstractValue:
                        self.pack_var_int(writer, type_info.abstract_value)

                    if type_info.tag_format_flags & TagFormatFlags.Members:
                        self.pack_var_int(writer, len(type_info.members))

                        for member in type_info.members:
                            self.pack_var_int(writer, member_names.index(member.name))
                            self.pack_var_int(writer, member.flags)
                            self.pack_var_int(writer, member.offset)
                            self.pack_var_int(writer, member.type_index)

                    if type_info.tag_format_flags & TagFormatFlags.Interfaces:
                        self.pack_var_int(writer, len(type_info.interfaces))

                        for interface in type_info.interfaces:
                            self.pack_var_int(writer, interface.type_index)
                            self.pack_var_int(writer, interface.flags)

            with self.pack_section(writer, "THSH"):
                hashed_types = [
                    (i + 1, type_info) for i, type_info in enumerate(self.type_info_dict.values()) if type_info.hsh
                ]
                hashed = []
                self.pack_var_int(writer, len(hashed_types))
                for i, type_info in hashed_types:
                    hashed.append((type_info.name, hex(writer.position), type_info.hsh))
                    self.pack_var_int(writer, i)
                    writer.pack("<I", type_info.hsh)
                if _DEBUG_HASH:
                    for h in sorted(hashed):
                        print(h[0], h[2])

            with self.pack_section(writer, "TPAD"):
                pass

    def pack_index_section(self, writer: BinaryWriter, data_start_offset: int):

        type_names = [""] + list(self.type_info_dict.keys())

        with self.pack_section(writer, "INDX", flag=False):

            with self.pack_section(writer, "ITEM"):

                # Null item. Counts toward indexing.
                writer.pad(12)

                for item in self.items[1:]:  # skip null item
                    type_index = type_names.index(item.hk_type.__name__)
                    writer.pack("<I", type_index | (0x10000000 if item.is_ptr else 0x20000000))
                    writer.pack("<I", item.absolute_offset - data_start_offset)
                    writer.pack("<I", item.length)

            with self.pack_section(writer, "PTCH"):
                patches_indices = [(type_names.index(name), offsets) for name, offsets in self._patches.items()]
                patches_indices.sort(key=lambda x: x[0])
                for type_index, offsets in patches_indices:
                    offsets = list(set(offsets))
                    offsets.sort()
                    writer.pack("<2I", type_index, len(offsets))
                    for offset in offsets:
                        writer.pack("<I", offset - data_start_offset)

    def pack_var_int(self, writer: BinaryWriter, value: int):
        if value < 0x80:
            writer.pack("B", value)
        elif value < 0x4000:
            writer.pack(">H", value | 0x8000)
        elif value < 0x200000:
            writer.pack("B", (value >> 16) | 0xC0)
            writer.pack(">H", value & 0xFFFF)
        elif value < 0x8000000:
            writer.pack(">I", value | 0xE0000000)

    @staticmethod
    def next_power_of_two(n):
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
