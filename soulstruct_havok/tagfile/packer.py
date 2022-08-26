from __future__ import annotations

import colorama
import typing as tp
from collections import deque
from contextlib import contextmanager

from soulstruct.utilities.binary import BinaryWriter

from soulstruct_havok.enums import TagFormatFlags
from soulstruct_havok.types.core import hk, hkArray_, TypeInfoGenerator
from soulstruct_havok.types.info import TypeInfo
from .structs import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.core import HKX


colorama.init()
GREEN = colorama.Fore.GREEN
RESET = colorama.Fore.RESET


_DEBUG_TYPES = False  # Type order has been confirmed as valid several times!
_DEBUG_SECTIONS = False
_DEBUG_HASH = False
_DEBUG_PRINT = True


class UniqueInstance:
    """Simple hashable container that wraps item instances to make them unique for later `TagFileItem` lookup."""

    def __init__(self, value: hk | str | list):
        self.value = value


class TagFilePacker:
    """Builds "tagfile" style Havok (e.g., for Dark Souls Remastered)."""

    class ItemInstanceQueue(deque[tuple[tp.Type[hk], tp.Union[hk, str, list]]]):
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
        self.items = [None]  # type: list[None | TagFileItem]  # first entry is always `None` for 1-indexing
        self.type_info_dict = {}
        self._patches = {}  # type: dict[str, list[int]]  # maps base type names to absolute item offsets using them

    def get_py_type(self, type_name: str) -> tp.Type[hk]:
        return getattr(self.hk_types_module, type_name)

    def build_type_info_dict(self):
        """Collects all `TypeInfo`s for types used by this file."""
        self.type_info_dict = TypeInfoGenerator(self.items[1:], self.hk_types_module).type_infos
        type_py_names = [""] + list(self.type_info_dict.keys())
        for type_info in self.type_info_dict.values():
            type_info.indexify(type_py_names)

        if _DEBUG_TYPES:
            lines = []
            for i, hk_type in enumerate(type_py_names[1:]):
                lines.append(f"{i + 1}: {hk_type}")
            types = "\n    ".join(lines)
            print(f"{GREEN}Final packed type list:\n    {types}{RESET}")

    def pack(self) -> bytes:
        """Pack a tagfile using the `hkRootLevelContainer` (`hkx.root`).

        First, we scan the full structure and collect types to write into the tagfile's TYPE section. During this, we
        also keep track of array and pointer types for re-use (though not sure exactly how unique these end up being,
        and it's probably only good for efficiency).
        """

        # self.hkx_types.convert_types_to_2015()  # TODO

        writer = BinaryWriter(big_endian=False)  # TODO: big_endian always false?

        with self.pack_section(writer, "TAG0", flag=False):

            with self.pack_section(writer, "SDKV"):
                writer.append(b"20150100")  # TODO: Always this version?

            with self.pack_section(writer, "DATA"):

                data_start_offset = writer.position
                self.items = [None]  # to mimic 1-indexing
                existing_items = {}

                # Dummy pointer item for root (`hkRootLevelContainer`).
                root_item = TagFileItem(hk_type=self.hkx.root.__class__, is_ptr=True, length=1)
                self.items.append(root_item)  # index 1, due to `None` at index 0
                root_item.writer = BinaryWriter()
                root_item.value = self.hkx.root

                # Master queue of `hkRefPtr` creation actions.
                ref_queue = deque([root_item])

                def write_item_data(item_):
                    if issubclass(item_.hk_type, hkArray_):
                        alignment = 16
                    else:
                        alignment = max(2, item_.get_item_hk_type(self.hk_types_module).alignment)
                    writer.pad_align(alignment)
                    item_.absolute_offset = writer.position
                    item_.finish_writer()
                    writer.append(item_.data)
                    for type_name, patch_offsets in item_.patches.items():
                        data_patch_offsets = [p + item_.absolute_offset - data_start_offset for p in patch_offsets]
                        self._patches.setdefault(type_name, []).extend(data_patch_offsets)

                while ref_queue:
                    ref_subqueue = {
                        "pointer": deque(), "array": deque(), "variant_name_string": deque(), "string": deque()
                    }
                    ref_item = ref_queue.popleft()
                    items_to_write = deque([ref_item])

                    # Pack `hkRefPtr` item and iterate through it (but not beyond members requiring new item creations)
                    # to accumulate item creation funcs into `ref_subqueue`.
                    ref_item.value.pack(ref_item, ref_item.value, self.items, existing_items, ref_subqueue)

                    # Array packing may create more items in the same subqueue, so we keep checking it.
                    while any(ref_subqueue.values()):
                        # Collected "pointer" item creation funcs are run immediately.
                        while ref_subqueue["pointer"]:
                            pointer_creation_func = ref_subqueue["pointer"].popleft()
                            new_ref_item = pointer_creation_func(ref_subqueue)  # does not pack to data
                            if new_ref_item:  # ignore existing items (`None` returned)
                                ref_queue.append(new_ref_item)
                                # NOT appended to `items_to_write`. It will be first in the writing queue when it is
                                # popped from `ref_queue`.

                        while ref_subqueue["array"]:
                            array_creation_func = ref_subqueue["array"].popleft()
                            # This creation func packs to data immediately, and may add more "pointer" creation funcs
                            # (or potentially "string" creation funcs) to this subqueue for the next pass.
                            array_item = array_creation_func(ref_subqueue)

                            if array_item.hk_type.__name__ == "hkArray[hkRootLevelContainerNamedVariant]":
                                # Do variant pointer items immediately. TODO: Set this up more nicely.
                                while ref_subqueue["pointer"]:
                                    pointer_creation_func = ref_subqueue["pointer"].popleft()
                                    new_ref_item = pointer_creation_func(ref_subqueue)  # does not pack to data
                                    if new_ref_item:  # ignore existing items (`None` returned)
                                        ref_queue.append(new_ref_item)

                            items_to_write.append(array_item)

                        for item_type in ("variant_name_string", "string"):
                            while ref_subqueue[item_type]:
                                string_creation_func = ref_subqueue[item_type].popleft()
                                # This creation func packs the string to data immediately and will never queue anything.
                                string_item = string_creation_func(ref_subqueue)  # takes argument for consistency
                                items_to_write.append(string_item)

                    for item in items_to_write:
                        write_item_data(item)

                # Final alignment.
                writer.pad_align(16)

            self.build_type_info_dict()

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

                    # TODO: hkReferencedObject and T* are swapped.

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

                # Null item. Counts toward indexing and corresponds to `None` being first element of `self.items`.
                writer.pad(12)

                for i, item in enumerate(self.items[1:]):  # skip null item
                    type_index = type_names.index(item.get_item_hk_type(self.hk_types_module).__name__)
                    type_index_with_ptr = type_index | (0x10000000 if item.is_ptr else 0x20000000)
                    item_relative_offset = item.absolute_offset - data_start_offset
                    item_length = item.length
                    writer.pack("<I", type_index_with_ptr)
                    writer.pack("<I", item_relative_offset)
                    writer.pack("<I", item_length)

            with self.pack_section(writer, "PTCH"):
                patches_indices = [(type_names.index(name), offsets) for name, offsets in self._patches.items()]
                patches_indices.sort(key=lambda x: x[0])
                for type_index, offsets in patches_indices:
                    offsets = list(set(offsets))
                    offsets.sort()
                    writer.pack("<2I", type_index, len(offsets))
                    for offset in offsets:
                        writer.pack("<I", offset)

    @staticmethod
    def pack_var_int(writer: BinaryWriter, value: int):
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
