from __future__ import annotations

__all__ = [
    "TagFilePacker",
]

import colorama
import typing as tp
from collections import deque
from contextlib import contextmanager

from soulstruct.utilities.binary import *

from soulstruct.havok.enums import TagFormatFlags, HavokModule
from soulstruct.havok.types.base import hkArray_
from soulstruct.havok.types.hk import hk
from soulstruct.havok.types.info import TypeInfo
from soulstruct.havok.types.type_info_generator import TypeInfoGenerator

from .structs import *

if tp.TYPE_CHECKING:
    from soulstruct.havok.core import HKX


colorama.just_fix_windows_console()
GREEN = colorama.Fore.GREEN
MAGENTA = colorama.Fore.LIGHTMAGENTA_EX
RED = colorama.Fore.RED
RESET = colorama.Fore.RESET


_DEBUG_TYPES = False  # Type order has been confirmed as valid several times!
_DEBUG_SECTIONS = False
_DEBUG_HASH = False


class TagFilePacker:
    """Builds "tagfile" style Havok (e.g., for Dark Souls Remastered)."""

    class ItemInstanceQueue(deque[tuple[type[hk], tp.Union[hk, str, list]]]):
        """Holds a deque of pairs of `hk` types and their associated instance values (`hk` instances, strings or lists)
        that are to be packed into items.

        The offset of the instance's item in the "DATA" section is reserved and filled later when the queue is
        processed and the `TagFileItem` created.
        """

    havok_module: HavokModule
    hkx: HKX
    items: list[None | TagFileItem]
    type_info_dict: dict[str, TypeInfo]

    # Maps base type names to absolute offsets of items using them.
    _patches: dict[str, list[int]]

    def __init__(self, hkx: HKX):
        self.havok_module = hkx.havok_module
        self.hkx = hkx
        self.items = [None]  # type: list[None | TagFileItem]  # first entry is always `None` for 1-indexing
        self.type_info_dict = {}
        self._patches = {}  # type: dict[str, list[int]]

    def build_type_info_dict(self, long_varints: bool):
        """Collects all `TypeInfo`s for types used by this file."""
        type_info_gen = TypeInfoGenerator(self.havok_module.get_submodule(), long_varints)
        self.type_info_dict = type_info_gen.generate_type_info_dict(self.items[1:])
        type_py_names = [""] + list(self.type_info_dict.keys())
        for type_info in self.type_info_dict.values():
            type_info.indexify(type_py_names)

        if _DEBUG_TYPES:
            lines = []
            for i, hk_type in enumerate(type_py_names[1:]):
                lines.append(f"{i + 1}: {hk_type}")
            types = "\n    ".join(lines)
            print(f"{GREEN}Final packed type list:\n    {types}{RESET}")

    def to_writer(
        self,
        hsh_overrides: dict[str, int] = None,
        byte_order: ByteOrder = ByteOrder.LittleEndian,
        long_varints: bool = True,
    ) -> BinaryWriter:
        """Pack a tagfile using the `hkRootLevelContainer` (`hkx.root`).

        First, we scan the full structure and collect types to write into the tagfile's TYPE section. During this, we
        also keep track of array and pointer types for re-use (though not sure exactly how unique these end up being,
        and it's probably only good for efficiency).
        """
        if hsh_overrides is None:
            hsh_overrides = {}

        writer = BinaryWriter(byte_order=byte_order)

        with self.pack_section(writer, "TAG0", flag=False):

            with self.pack_section(writer, "SDKV"):
                writer.append(self.hkx.hk_version.encode())

            with self.pack_section(writer, "DATA"):

                with hk.set_havok_module(self.havok_module):
                    data_start_offset = self.pack_data_section(writer)
                    self.build_type_info_dict(long_varints)

            self.pack_type_section(writer, hsh_overrides)

            self.pack_index_section(writer, data_start_offset)

        return writer

    def pack_data_section(self, writer: BinaryWriter) -> int:
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
            """Align master writer, set item's offset within it, append item data, and collect patch offsets."""
            item_hk_data_type = item_.get_item_hk_data_type()
            if issubclass(item_.hk_type, hkArray_) and item_hk_data_type.__name__ != "hkRootLevelContainerNamedVariant":
                alignment = 16
            else:
                alignment = max(2, item_hk_data_type.alignment)

            writer.pad_align(alignment)
            item_.absolute_offset = writer.position
            item_.finish_writer()
            writer.append(item_.data)
            for type_name, patch_offsets in item_.patches.items():
                data_patch_offsets = [p + item_.absolute_offset - data_start_offset for p in patch_offsets]
                self._patches.setdefault(type_name, []).extend(data_patch_offsets)

        while ref_queue:
            ref_subqueues = TagItemCreationQueues(writer.byte_order)
            ref_item = ref_queue.popleft()
            items_to_write = deque([ref_item])

            # Pack `hkRefPtr` item and iterate through it (but not beyond members requiring new item creations)
            # to accumulate item creation funcs into `ref_subqueue`.
            ref_item.value.pack_tagfile(ref_item, ref_item.value, self.items, existing_items, ref_subqueues)

            # Array packing may create more items in the same subqueue, so we keep checking it.
            while ref_subqueues.any():
                # Collected "pointer" item creation funcs are run immediately.
                while ref_subqueues.pointers:
                    pointer_creation_func = ref_subqueues.pointers.popleft()
                    new_ref_item = pointer_creation_func(ref_subqueues)  # does not pack to data
                    if new_ref_item:  # ignore existing items (`None` returned)
                        ref_queue.append(new_ref_item)
                        # NOT appended to `items_to_write`. It will be first in the writing queue when it is
                        # popped from `ref_queue`.

                while ref_subqueues.arrays:
                    array_creation_func = ref_subqueues.arrays.popleft()
                    # This creation func packs to data immediately, and may add more "pointer" creation funcs
                    # (or potentially "string" creation funcs) to this subqueue for the next pass.
                    array_item = array_creation_func(ref_subqueues)

                    if array_item.hk_type.__name__ == "hkArray[hkRootLevelContainerNamedVariant]":
                        # Do variant pointer items immediately. TODO: Set this up more nicely.
                        while ref_subqueues.pointers:
                            pointer_creation_func = ref_subqueues.pointers.popleft()
                            new_ref_item = pointer_creation_func(ref_subqueues)  # does not pack to data
                            if new_ref_item:  # ignore existing items (`None` returned)
                                ref_queue.append(new_ref_item)

                    items_to_write.append(array_item)

                for item_type in ("variant_name_strings", "strings"):
                    queue = getattr(ref_subqueues, item_type)
                    while queue:
                        string_creation_func = queue.popleft()
                        # This creation func packs the string to data immediately and will never queue anything.
                        string_item = string_creation_func(ref_subqueues)  # takes argument for consistency
                        items_to_write.append(string_item)

            for item in items_to_write:
                write_item_data(item)

        # Final alignment.
        writer.pad_align(16)

        return data_start_offset

    @contextmanager
    def pack_section(self, writer: BinaryWriter, magic: str, flag=True):

        section_start = writer.position
        if _DEBUG_SECTIONS:
            print(f"Section {magic} start: {hex(writer.position)}")

        section_start_offset = writer.position
        writer.reserve(f"{magic}_size", ">I")  # section size will be filled here later
        writer.append(magic[:4].encode("utf-8"))
        try:
            yield
        finally:
            writer.pad_align(4)
            section_size = (writer.position - section_start_offset) | (0x40_00_00_00 if flag else 0x0)
            writer.fill(f"{magic}_size", section_size)

            if _DEBUG_SECTIONS:
                print(f"  Section {magic} end: {hex(writer.position)} ({hex(writer.position - section_start)})")

    def pack_type_section(self, writer: BinaryWriter, hsh_overrides: dict[str, int]):

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

                # Inexplicably, `hkReferencedObject` and the `T*` that comes after it (in TNAM order) are swapped here.
                tbod_type_infos = [(i, t) for i, t in enumerate(self.type_info_dict.values())]
                try:
                    hk_referenced_object = [(i, t) for i, t in tbod_type_infos if t.name == "hkReferencedObject"][0]
                except IndexError:
                    pass
                else:
                    j = tbod_type_infos.index(hk_referenced_object)
                    t_star = tbod_type_infos[j + 1]
                    if t_star[1].name == "T*" and t_star[1].pointer_type_py_name == "hkReferencedObject":
                        tbod_type_infos[j:j + 2] = t_star, hk_referenced_object  # swap

                for i, type_info in tbod_type_infos:

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
                        # Byte size and alignment of pointers (-1) is resolved here.
                        if type_info.byte_size == -1:
                            byte_size = 8 if writer.long_varints else 4
                        else:
                            byte_size = type_info.byte_size
                        if type_info.alignment == -1:
                            alignment = 8 if writer.long_varints else 4
                        else:
                            alignment = type_info.alignment
                        self.pack_var_int(writer, byte_size)
                        self.pack_var_int(writer, alignment)

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
                # All hashes are taken from unpacked `hsh_overrides`, unless they are new types that did not exist
                # in the unpacked file (rare), in which case we must use the best guess stored in Soulstruct.
                # Note that hashes for the same types (including primitive types) vary across files, so beware.

                # Hash order (thankfully) does not seem to matter, and it's hard to tell exactly how the original files
                # are ordering it (similar to type order but not quite identical). So we just match type order.

                # TODO: Could at least match `hsh_overrides` order.
                hashed_types = [
                    (i + 1, type_info) for i, type_info in enumerate(self.type_info_dict.values())
                    if hsh_overrides.get(type_info.get_full_py_name(), type_info.hsh) is not None
                ]
                self.pack_var_int(writer, len(hashed_types))
                hashed = []
                if _DEBUG_HASH:
                    print(f"{MAGENTA}Packed hashes:{RESET}")
                for i, type_info in hashed_types:
                    full_py_name = type_info.get_full_py_name()
                    self.pack_var_int(writer, i)
                    # Use override if it exists, otherwise use original hash in Python class (`type_info.hsh`).
                    hsh = hsh_overrides.get(full_py_name, type_info.hsh)
                    writer.pack("<I", hsh)
                    if _DEBUG_HASH:
                        print(
                            f"    {MAGENTA}`{full_py_name}`: {hsh}"
                            f"{f' {RED}<OVERRIDE>' if full_py_name in hsh_overrides else ''}{RESET}"
                        )
                        hashed.append((hsh, full_py_name, full_py_name in hsh_overrides))
                if _DEBUG_HASH:
                    print(f"{MAGENTA}Packed hashes (sorted):{RESET}")
                    for type_hsh, type_name, is_override in sorted(hashed, key=lambda x: x[0]):
                        print(
                            f"    {MAGENTA}`{type_name}`: {type_hsh}"
                            f"{f' {RED}<OVERRIDE>' if is_override else ''}{RESET}"
                        )

            with self.pack_section(writer, "TPAD"):
                pass

    def pack_index_section(self, writer: BinaryWriter, data_start_offset: int):

        type_names = [""] + list(self.type_info_dict.keys())

        with self.pack_section(writer, "INDX", flag=False):

            with self.pack_section(writer, "ITEM"):

                # Null item. Counts toward indexing and corresponds to `None` being first element of `self.items`.
                writer.pad(12)

                for i, item in enumerate(self.items[1:]):  # skip null item
                    type_index = type_names.index(item.get_item_hk_data_type().__name__)
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
