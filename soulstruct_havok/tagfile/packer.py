from __future__ import annotations

import typing as tp
from collections import deque
from contextlib import contextmanager

from colorama import init as colorama_init, Fore
from soulstruct.utilities.binary import BinaryWriter

from .structs import HKXItem
from ..enums import TagDataType, TagFormatFlags
from ..nodes import HKXNode, HKXArrayNode, HKXTupleNode, NodeTypeReindexer
from ..types import HKXType, HKXTypeList

if tp.TYPE_CHECKING:
    from ..core import HKX


colorama_init()


_DEBUG_SECTIONS = False
_DEBUG_HASH = False
_DEBUG_PRINT = ["XXX"]


class HKXTagFilePacker:
    """The node types used by this packer are loaded independently of the node types that are already attached to the
    `HKXNode`s in the passed `HKX`. The non-backported types used for packing tagfiles are found by looking up the
    matching index to the based on their index in the list.
    """

    class ItemNodeQueue(deque[tuple[HKXType, tp.Optional[str], tp.Optional[HKXNode]]]):
        """Holds a list of nodes that are to be packed into items.

        Byte-perfect writing here requires finesse, because `HKXItem` indices are recorded as members are encountered,
        but the instances/indices themselves are created for Array and Pointer members before String members. The node's
        item offset in the "DATA" section is reserved and filled later when the queue is processed (with Arrays and
        Pointers done first) and the `HKXItem` created.

        This is handled in the packer by iterating over the queue once to create items, with Arrays/Pointers created
        before Strings, then iterating over the queue again to actually unpack those items' nodes further.

        NEW: A `None` is inserted between each unpacked item, because it turns out that type rearrangement only occurs
        WITHIN each item, not across them.
        """

    hkx_items: list[HKXItem]
    hkx_types: HKXTypeList

    def __init__(self, hkx: HKX):
        self.hkx = hkx
        self.hkx_items = [None]  # type: list[tp.Optional[HKXItem]]  # first entry is `None`
        self.hkx_types = HKXTypeList([])
        self._node_items = {}  # type: dict[HKXNode, HKXItem]  # for later unpacking
        self._existing_object_items = {}  # type: dict[HKXNode, HKXItem]  # for re-using object-level items
        self._patches = {}  # type: dict[HKXType, list[int]]

    def pack(self) -> bytes:
        """Node types are written directly into tagfiles, so we scan all nodes for them and explicitly convert them to
        2015 versions rather than loading the full type database."""

        self.hkx_types = NodeTypeReindexer(self.hkx.hkx_types, self.hkx.root).reindex()

        # TODO: This entire class is byte-perfect except for the ordering of hashes. They seem to be ordered in a
        #  similar way to how items are ordered (arrays/pointers before strings, level by level) but I can't quite
        #  figure it out and it's barely worth it, of course.

        # TODO:
        #   UPDATE: Actually, the above is only true for Skeleton.HKX files. It's not true for animations, because the
        #   item ordering is weird and type-specific, and I think ragdoll files are still crashing.

        # self.hkx_types.convert_types_to_2015()  # TODO

        writer = BinaryWriter(big_endian=False)  # TODO: always false?

        with self.pack_section(writer, "TAG0", flag=False):

            with self.pack_section(writer, "SDKV"):
                writer.append(b"20150100")  # TODO: Always this version?

            with self.pack_section(writer, "DATA"):
                data_start_offset = writer.position
                self.create_root_item(self.hkx.root)
                self.object_queue = deque([self.hkx.root])
                self.packed_objects = []
                while self.object_queue:
                    obj_node = self.object_queue.popleft()
                    if obj_node is not self.hkx.root:
                        self.packed_objects.append(obj_node.value)
                    root_item_queue = self.ItemNodeQueue([(self.hkx_types["hkRootLevelContainer"], obj_node)])
                    self.pack_queued_items(writer, root_item_queue, is_object=True)

                writer.pad_align(16)

            self.pack_type_section(writer)
            self.pack_index_section(writer, data_start_offset)

        return writer.finish()

    @contextmanager
    def pack_section(self, writer: BinaryWriter, magic: str, flag=True):

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
                print(f"  Section {magic} end: {hex(writer.position)}")

    def pack_type_section(self, writer: BinaryWriter):

        with self.pack_section(writer, "TYPE", flag=False):

            with self.pack_section(writer, "TPTR"):
                # This pointer section is simply not used.
                writer.pad(8 * len(self.hkx_types))

            type_names = []
            member_names = []
            for hkx_type in self.hkx_types:
                if hkx_type.name not in type_names:
                    type_names.append(hkx_type.name)

                for template in hkx_type.templates:
                    if template.name not in type_names:
                        type_names.append(template.name)

                for member in hkx_type.members:
                    if member.name not in member_names:
                        member_names.append(member.name)

            with self.pack_section(writer, "TSTR"):
                writer.append(("\0".join(type_names) + "\0").encode("utf-8"))

            with self.pack_section(writer, "TNAM"):
                self.pack_var_int(writer, len(self.hkx_types))
                for hkx_type in self.hkx_types:
                    self.pack_var_int(writer, type_names.index(hkx_type.name))
                    self.pack_var_int(writer, len(hkx_type.templates))
                    for template in hkx_type.templates:
                        self.pack_var_int(writer, type_names.index(template.name))
                        if template.type_index:
                            self.pack_var_int(writer, template.type_index)
                        else:
                            self.pack_var_int(writer, template.value)

            with self.pack_section(writer, "FSTR"):
                writer.append(("\0".join(member_names) + "\0").encode("utf-8"))

            with self.pack_section(writer, "TBOD"):
                # "Type body" section, where everything about a type other than its name and templates is defined.

                # For some god-forsaken reason, the pointer type of `hkRefVariant` ("T*") has its information stored
                # here before the reference type (`hkReferencedObject`). The queue below is constructed to handle that.
                # Of course, we could ignore it, but byte-perfect file writing is too seductive to pass up, and this is
                # the only weird case. The ordering is otherwise identical to the "TNAM" type definition section.

                try:
                    hk_referenced_object_index = self.hkx_types.get_type_index("hkReferencedObject")
                    hkx_type_queue = (
                        self.hkx_types[1:hk_referenced_object_index] +
                        [self.hkx_types[hk_referenced_object_index + 1]] +  # T*
                        [self.hkx_types[hk_referenced_object_index]] +   # hkReferencedObject
                        self.hkx_types[hk_referenced_object_index + 2:]
                    )
                except KeyError:
                    # Very unusual for this type to be missing.
                    hkx_type_queue = self.hkx_types

                for hkx_type in hkx_type_queue:

                    self.pack_var_int(writer, self.hkx_types.index(hkx_type))
                    self.pack_var_int(writer, hkx_type.parent_type_index)
                    self.pack_var_int(writer, hkx_type.tag_format_flags)

                    if hkx_type.tag_format_flags & TagFormatFlags.SubType:
                        self.pack_var_int(writer, hkx_type.tag_type_flags)

                    if hkx_type.tag_format_flags & TagFormatFlags.Pointer:
                        self.pack_var_int(writer, hkx_type.pointer_type_index)

                    if hkx_type.tag_format_flags & TagFormatFlags.Version:
                        self.pack_var_int(writer, hkx_type.version)

                    if hkx_type.tag_format_flags & TagFormatFlags.ByteSize:
                        self.pack_var_int(writer, hkx_type.byte_size)
                        self.pack_var_int(writer, hkx_type.alignment)

                    if hkx_type.tag_format_flags & TagFormatFlags.AbstractValue:
                        self.pack_var_int(writer, hkx_type.abstract_value)

                    if hkx_type.tag_format_flags & TagFormatFlags.Members:
                        self.pack_var_int(writer, len(hkx_type.members))

                        for member in hkx_type.members:
                            self.pack_var_int(writer, member_names.index(member.name))
                            self.pack_var_int(writer, member.flags)
                            self.pack_var_int(writer, member.offset)
                            self.pack_var_int(writer, member.type_index)

                    if hkx_type.tag_format_flags & TagFormatFlags.Interfaces:
                        self.pack_var_int(writer, len(hkx_type.interfaces))

                        for interface in hkx_type.interfaces:
                            self.pack_var_int(writer, interface.type_index)
                            self.pack_var_int(writer, interface.flags)

            with self.pack_section(writer, "THSH"):
                hashed_hkx_types = [hkx_type for hkx_type in self.hkx_types if hkx_type.hsh]
                hashed = []
                self.pack_var_int(writer, len(hashed_hkx_types))
                for hkx_type in hashed_hkx_types:
                    hashed.append((hkx_type.name, hex(writer.position), hkx_type.hsh))
                    self.pack_var_int(writer, self.hkx_types.index(hkx_type))
                    writer.pack("<I", hkx_type.hsh)
                if _DEBUG_HASH:
                    for h in sorted(hashed):
                        print(h[0], h[2])

            with self.pack_section(writer, "TPAD"):
                pass

    def pack_index_section(self, writer: BinaryWriter, data_start_offset: int):

        with self.pack_section(writer, "INDX", flag=False):

            with self.pack_section(writer, "ITEM"):

                # Null item. Counts toward indexing.
                writer.pad(12)

                for item in self.hkx_items[1:]:  # skip null item
                    hkx_type_index = self.hkx_types.index(item.hkx_type)
                    writer.pack("<I", hkx_type_index | (0x10000000 if item.is_ptr else 0x20000000))
                    writer.pack("<I", item.absolute_offset - data_start_offset)
                    writer.pack("<I", len(item.node_value))

            with self.pack_section(writer, "PTCH"):
                patches_indices = [(self.hkx_types.index(key), value) for key, value in self._patches.items()]
                patches_indices.sort(key=lambda x: x[0])
                for hkx_type_index, offsets in patches_indices:
                    offsets = list(set(offsets))
                    offsets.sort()
                    writer.pack("<2I", hkx_type_index, len(offsets))
                    for offset in offsets:
                        writer.pack("<I", offset - data_start_offset)

    def pack_queued_items(
        self, writer: BinaryWriter, item_queue: ItemNodeQueue, is_object=False, indent=0
    ):
        """Create and then pack items from queued Array/Pointer/String nodes.

        Any additional items queued during the packing process are queued separately, and this method is recurred on
        them afterward - no lower-level items are ever created before the current level is finished.

        Note that items are created in (Pointer, Array, String) order, but then the item nodes themselves are further
        unpacked in (Array, String, Pointer) order. Of course, this doesn't ALWAYS match vanilla files - the spline-
        compressed animation type, for example, processes its members in straightforward order, for example. But this
        order seems to work most of the time and leads to byte-perfect writes for DSR skeleton HKX files. This decision,
        of course, does NOT affect functionality at all.

        One exception: the members for `hkRootLevelContainer::NamedVariant` Class nodes are unpacked such that all the
        "name" String members of the "namedVariant" array are unpacked before all the "className" strings. This is
        only noticeable in the large CHRBND HKX files, where there's actually more than one "namedVariant".
        """

        ind = " " * indent

        if is_object:
            creation_queue = deque()
            packing_queue = deque([node for _, node in item_queue if node is not None])
        else:
            creation_queue = deque()
            packing_queue = deque()

            item_pointers = deque()
            item_arrays = deque()
            item_strings = deque()
            item_variant_name_strings = deque()  # created before other strings (in practice, just "className")

            while item_queue:
                owner_type, owner_member, node = item_queue.popleft()
                if node is None:
                    creation_queue.extend(item_pointers + item_arrays + item_variant_name_strings + item_strings)
                    packing_queue.extend(item_arrays + item_variant_name_strings + item_strings)
                    item_pointers.clear()
                    item_arrays.clear()
                    item_strings.clear()
                    continue

                node_data_type = node.get_base_type(self.hkx_types).tag_data_type
                if node_data_type == TagDataType.Pointer:
                    item_pointers.append(node)
                elif node_data_type == TagDataType.Array:
                    item_arrays.append(node)
                elif node_data_type == TagDataType.String:
                    if owner_type.name_without_colons == "hkRootLevelContainerNamedVariant" and owner_member == "name":
                        item_variant_name_strings.append(node)
                    else:
                        item_strings.append(node)
                else:
                    raise TypeError(f"Invalid queued item node type: {node_data_type}")

        for node in creation_queue:

            # TODO: To achieve byte-perfect writes, type hashing needs to be done in approximately this order, but with
            #  nodes WITHIN these items found as well.

            # Create new `HKXItem` (or retrieve existing one for object pointers).
            item = self.create_item_from_node(node, indent=indent + 4)
            if item is None:
                raise AssertionError(f"Item was None.")
            type_patches = self._patches.setdefault(node.get_base_type(self.hkx_types), [])
            reserved_offset = writer.reserved[f"{id(node)}ItemIndex"][0]
            type_patches.append(reserved_offset)
            node_type = node.get_type(self.hkx_types)
            item_index = self.hkx_items.index(item)
            if not _DEBUG_PRINT or item.hkx_type in _DEBUG_PRINT:
                print(
                    f"{ind}{Fore.RED}Filling {node_type.name} ITEM INDEX: {item_index} ({hex(item_index)}) "
                    f"{Fore.CYAN}at {hex(reserved_offset)}{Fore.RESET}"
                )
            writer.fill(f"{id(node)}ItemIndex", item_index)

        item_sub_queue = self.ItemNodeQueue()

        # Items' nodes are further unpacked in the order they occurred.
        for node in packing_queue:
            item = self._node_items[node]  # freshly created above

            if not _DEBUG_PRINT or item.hkx_type.name in _DEBUG_PRINT:
                print(
                    f"{ind}Packing queued item node ({self.hkx_items.index(item)}): "
                    f"{node.get_type_name(self.hkx_types)} | {item.hkx_type.name}"
                )

            item_base_type = item.hkx_type.get_base_type(self.hkx_types)

            if item.data_type == TagDataType.Array:
                # Array items always align to 16, regardless of element size/alignment.
                alignment = 16
            else:
                # Any other item alignment is no less than 2.
                alignment = max(2, item_base_type.alignment)

            writer.pad_align(alignment)

            item.absolute_offset = writer.position

            if item.simple_array_flags is not None:
                array_size = len(node.value)
                if item.simple_array_flags & 0xFF == TagDataType.Bool:
                    fmt = TagDataType.get_int_fmt(item.simple_array_flags, count=array_size)
                elif item.simple_array_flags & 0xFF == TagDataType.Int:
                    signed = item.simple_array_flags & TagDataType.IsSigned
                    fmt = TagDataType.get_int_fmt(item.simple_array_flags, signed=signed, count=array_size)
                elif item.simple_array_flags == TagDataType.Float | TagDataType.Float32:
                    fmt = f"<{array_size}f"
                else:
                    raise TypeError(
                        f"Invalid simple Array flags (must be Bool, Int, or Float32 type): {item.simple_array_flags}"
                    )
                writer.pack(fmt, *node.value)
            else:
                for i in range(len(item.node_value)):
                    self.pack_node(
                        writer,
                        node=item.node_value[i],
                        offset=item.absolute_offset + i * item_base_type.byte_size,
                        owner_type=item.hkx_type,
                        item_queue=item_sub_queue,
                        indent=indent + 4,
                    )

            item_sub_queue.append((item.hkx_type, None, None))

        if item_sub_queue:
            self.pack_queued_items(writer, item_sub_queue, indent=indent + 4)

    def pack_node(
        self,
        writer: BinaryWriter,
        node: HKXNode,
        item_queue: ItemNodeQueue,
        offset=0,
        owner_type: tp.Optional[HKXType] = None,
        owner_member: tp.Optional[str] = None,
        indent=0,
        debug_print=False,
    ):
        if offset == 0:
            offset = writer.position
        else:
            while writer.position < offset:
                writer.pad(1)

        original_hkx_type = node.get_type(self.hkx_types)
        hkx_type = original_hkx_type.get_base_type(self.hkx_types)

        ind = " " * indent
        if debug_print and hkx_type.name not in {"char", "unsigned char"}:
            print_t = hkx_type.name if original_hkx_type is hkx_type else f"{original_hkx_type.name} ({hkx_type.name})"
            size = len(node.value) if isinstance(node.value, (list, tuple, dict)) else 0
            if isinstance(node.value, list):
                if isinstance(node, HKXArrayNode):
                    print_v = f"[size {size}]" if size >= 5 else node.value
                else:
                    print_v = f"[size {size}]" if size >= 5 else [n.value for n in node.value]
            elif isinstance(node.value, tuple):
                if isinstance(node, HKXTupleNode):
                    print_v = f"(size {size})" if size >= 5 else node.value
                else:
                    print_v = f"(size {size})" if size >= 5 else tuple(n.value for n in node.value)
            elif isinstance(node.value, dict):
                print_v = f"{{size {size}}}" if size >= 5 else {k: v.value for k, v in node.value.items()}
            else:
                print_v = repr(node.value)
            print(
                f"{ind}{Fore.YELLOW}Packing node: {print_t} "
                f"| {Fore.GREEN}{hkx_type.tag_data_type.name} "
                f"| {Fore.CYAN}Position: {hex(writer.position)}{Fore.RESET} "
                f"| {Fore.BLUE}Value: {print_v}{Fore.RESET}"
            )

        if hkx_type.tag_data_type == TagDataType.Bool:
            writer.pack(TagDataType.get_int_fmt(hkx_type.tag_type_flags), node.value)

        elif hkx_type.tag_data_type in {TagDataType.String, TagDataType.Pointer, TagDataType.Array}:

            if node.value is None or (isinstance(node.value, (list, tuple, dict)) and not node.value):
                pass  # skip null node
            elif node in self._node_items:
                # Write index of existing item.
                if debug_print:
                    print(
                        f"{ind}{Fore.RED}Packing node's existing item index: "
                        f"{self.hkx_items.index(self._node_items[node])}{Fore.RESET}"
                    )
                writer.pack("<I", self.hkx_items.index(self._node_items[node]))
            else:
                # Reserve offset and queue item node for packing.
                if debug_print:
                    print(f"{ind}{Fore.RED}Reserving node item index: {Fore.CYAN}{hex(writer.position)}{Fore.RESET}")
                writer.reserve(f"{id(node)}ItemIndex", "<I")
                item_queue.append((owner_type, owner_member, node))

        elif hkx_type.tag_data_type == TagDataType.Int:
            fmt = TagDataType.get_int_fmt(hkx_type.tag_type_flags, signed=node.value < 0)
            try:
                writer.pack(fmt, node.value)
            except Exception:
                print(hkx_type.name, hkx_type.tag_type_flags, fmt, f"value = {node.value}")
                raise

        # 32-bit floats only. Other float sizes (16, 8 bits) have a member integer holding their binary representation.
        elif hkx_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
            writer.pack("<f", node.value)

        # Captures non-32-bit floats.
        elif hkx_type.tag_data_type in {TagDataType.Class, TagDataType.Float}:

            for i, member in enumerate(hkx_type.get_all_members(self.hkx_types)):
                if not _DEBUG_PRINT or hkx_type.name in _DEBUG_PRINT or _DEBUG_PRINT == "Class":
                    print(f"{ind}  {Fore.MAGENTA}\"{member.name}\"{Fore.RESET}")
                # TODO: How to handle superfluous node member keys?
                if member.name in node.value:
                    self.pack_node(
                        writer,
                        node=node.value[member.name],
                        item_queue=item_queue,
                        offset=offset + member.offset,
                        owner_type=original_hkx_type,
                        owner_member=member.name,
                        indent=indent + 4,
                        debug_print=not _DEBUG_PRINT or hkx_type.name in _DEBUG_PRINT or _DEBUG_PRINT == "Class",
                    )
                else:
                    raise KeyError(f"Member key {member.name} missing from node (base type {hkx_type.name}).")

        elif hkx_type.tag_data_type == TagDataType.Tuple:
            if isinstance(node, HKXTupleNode):
                tuple_size = len(node.value)
                element_type_flags = hkx_type.get_pointer_base_type(self.hkx_types).tag_type_flags
                if element_type_flags & 0xFF == TagDataType.Bool:
                    fmt = TagDataType.get_int_fmt(element_type_flags, count=tuple_size)
                elif element_type_flags & 0xFF == TagDataType.Int:
                    signed = element_type_flags & TagDataType.IsSigned
                    fmt = TagDataType.get_int_fmt(element_type_flags, signed=signed, count=tuple_size)
                elif element_type_flags & 0xFF == TagDataType.Float:
                    fmt = f"<{tuple_size}f"
                else:
                    raise TypeError(
                        f"Invalid simple Tuple flags (must be Bool, Int, or Float type): {element_type_flags}"
                    )
                writer.pack(fmt, *node.value)
            else:
                for i in range(hkx_type.tuple_size):
                    self.pack_node(
                        writer,
                        node.value[i],
                        item_queue=item_queue,
                        offset=offset + i * hkx_type.get_pointer_base_type(self.hkx_types).byte_size,
                        owner_type=original_hkx_type,
                        indent=indent + 4,
                        debug_print=not _DEBUG_PRINT or hkx_type.name in _DEBUG_PRINT
                    )

        writer.pad((offset + hkx_type.byte_size) - writer.position)

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

    def create_root_item(self, node: HKXNode):
        """Create a fake pointer-type `HKXItem` for the root node ("hkRootLevelContainer")."""
        item_hkx_type = node.get_type(self.hkx_types)
        item_value = [node]  # fake pointer
        item = HKXItem(item_hkx_type, is_ptr=True, nodes=item_value, data_type=TagDataType.Pointer)
        self.hkx_items.append(item)
        self._node_items[node] = item

    def create_item_from_node(self, node: HKXNode, indent=0) -> tp.Optional[HKXItem]:
        """Create a `HKXItem`, which is the binary object that will actually be packed.

        Each of these items corresponds to a String, Pointer, or Array node. Primitive "nods" are packed into their
        parent items. (Note that each item's `value` is always a list of nodes, even though it will always be just one
        node for String and Pointer nodes, so that the node packer can use the same iteration code.)
        """
        node_base_type = node.get_base_type(self.hkx_types)

        if node_base_type.tag_data_type == TagDataType.String:
            # Now supports Shift-JIS encoding.
            item_hkx_type = self.hkx_types["char"]
            char_array = bytearray(node.value.encode("shift_jis_2004") + b"\0")
            item_value = [HKXNode(char, self.hkx_types.get_type_index("char")) for char in char_array]
            item = HKXItem(item_hkx_type, nodes=item_value, data_type=TagDataType.String)

        elif node_base_type.tag_data_type == TagDataType.Pointer:
            # If pointer points to an object, retrieve the existing item for it.
            if node.value in self._existing_object_items:
                return self._existing_object_items[node.value]

            item_hkx_type = node.value.get_type(self.hkx_types)
            item_value = [node.value]
            item = HKXItem(item_hkx_type, is_ptr=True, nodes=item_value, data_type=TagDataType.Pointer)
            self.object_queue.append(node)
            self._existing_object_items[node.value] = item

        elif node_base_type.tag_data_type == TagDataType.Array:
            # Node `value` could be a list of Python literals for `HKXArrayNode` nodes. This is handled at pack time.
            if isinstance(node, HKXArrayNode):
                simple_array_flags = node_base_type.get_pointer_base_type(self.hkx_types).tag_type_flags
            else:
                simple_array_flags = None
            item_hkx_type = node.get_base_type(self.hkx_types).get_pointer_type(self.hkx_types)
            item_value = node.value
            item_is_ptr = node_base_type.tag_data_type == TagDataType.Pointer
            item = HKXItem(
                item_hkx_type,
                is_ptr=item_is_ptr,
                nodes=item_value,
                data_type=TagDataType.Array,
                simple_array_flags=simple_array_flags,
            )

        else:
            raise TypeError(f"Cannot create item from node type: {node_base_type.name}")

        self._node_items[node] = item

        self.hkx_items.append(item)
        if not _DEBUG_PRINT or item_hkx_type.name in _DEBUG_PRINT:
            print(
                f"{' ' * indent}CREATED ITEM with type: {item.hkx_type.name} (index {len(self.hkx_items) - 1}) "
                f"from node with type {node.get_type_name(self.hkx_types)}"
            )

        return item

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
