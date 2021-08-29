from __future__ import annotations

__all__ = [
    "HKXNode",
    "HKXArrayNode",
    "HKXTupleNode",
    "NodeCollector",
    "NodeFinder",
    "NodeTypeReindexer",
    "NodeTypeReassigner",
    "NodeComparer",
]

import copy
import logging
import math
import typing as tp
from collections import deque

from colorama import init as colorama_init, Fore

from .enums import TagDataType
from .objects import HKXObject
from .types import HKXType, HKXTypeList

if tp.TYPE_CHECKING:
    from .core import HKX


_LOGGER = logging.getLogger(__name__)

colorama_init()


class HKXNode:
    """Primitive node that appears in HKX (both formats). Holds an index into a `HKXTypeList` so its type can be used
    for packing later (after possible type conversion).

    The `value` of the node could be:
        - a bool, int, or float (Bool/Int/Float type)
        - a string (String type)
        - a single node (Pointer type)
        - a dictionary mapping member names to nodes (Class type)
        - a list of other nodes (Array type)
        - a tuple of other nodes (Tuple type)

    Note that for dictionary (Class) nodes, the order of the dictionary keys is NOT reliable, as they may be modified
    while converting between Havok versions. Always iterate over the `members` attribute of the node's type to get them
    in proper order.

    See also `HKXArrayNode` and `HKXTupleNode` subclasses below, which simplify Array and Tuple type nodes when their
    contents are primitive Bool/Int/Float types (which spares Python from needing to create tens of thousands of nodes
    for large but simple numeric arrays).
    """

    SUBCLASS = ""  # could be any

    type_index: int
    value: tp.Union[bool, int, float, str, HKXNode, dict[str, HKXNode], list[HKXNode, ...], tuple[HKXNode, ...]]

    _py_object: tp.Optional[HKXObject]

    def __init__(self, value, type_index: int):
        self.type_index = type_index
        if not isinstance(self.type_index, int):
            raise ValueError(f"Node must be given a type index (integer), not: {type_index}.")
        self.value = value
        self._py_object = None

    def __getitem__(
        self, index_or_member_name: tp.Union[int, str]
    ) -> tp.Union[
        bool, int, float, str, HKXNode,
        list[tp.Union[bool, int, float], ...],
        tuple[tp.Union[bool, int, float], ...],
    ]:
        """Convenient access for exploring the node structure in a way that doesn't spread the word `value` all over
        your code dozens of times.

        - Array/Tuple node values can be indexed directly by integers.
        - Class node values can be keyed by member names.

        In either case, if the returned node is a Pointer node, it will be "skipped" by this method (i.e. its own
        `value` will be returned instead, and so on until a non-Pointer is found). Finally, if the reached node is
        a primitive (Bool, Int, Float, or String), that primitive value will be returned to spare you the final `.value`
        attribute expression. Similarly, simple Array/Tuple primitive subclasses will return the primitive list/tuple,
        so you can e.g. easily do something like `translate = Vector4(node["translate"])`.

        Also note that the simple Array/Tuple subclasses will return primitive values with this method (from integer
        indices obviously), not a node.
        """
        if isinstance(self.value, (list, tuple)):
            index = index_or_member_name
            if not isinstance(index, int):
                raise TypeError(f"Array/Tuple node must be indexed by an integer, not: {index}")
            try:
                node = self.value[index]
            except IndexError:
                raise IndexError(f"Invalid index for Array/Tuple node of length {len(self.value)}: {index}")
        elif isinstance(self.value, dict):
            name = index_or_member_name
            if not isinstance(name, str):
                raise TypeError(f"Class node must be indexed by a member name string, not: {name}")
            try:
                node = self.value[name]
            except KeyError:
                raise KeyError(f"Invalid member name for Class node: {name}. Members: {self.value.keys()}")
        else:
            raise TypeError(
                f"Cannot index node with value type {type(self.value)}. Only Array/Tuple (by index) and Class (by "
                f"member name) can be accessed this way."
            )
        if not isinstance(node, HKXNode):
            return node  # primitive (this is a simple Array/Tuple node)
        if isinstance(node, (HKXArrayNode, HKXTupleNode)):
            return node.value  # return simple list/tuple
        while isinstance(node.value, HKXNode):
            node = node.value  # skip any pointers
        if isinstance(node.value, (bool, int, float, str)):
            return node.value  # primitive
        return node  # actual node

    def get_py_object(self, object_class: tp.Type[HKXObject]) -> tp.Optional[HKXObject]:
        if self._py_object is None:
            if self.value is None:
                self._py_object = None
            else:
                self._py_object = object_class(self)
        return self._py_object

    def set_py_object(self, py_object: HKXObject):
        self._py_object = py_object

    def get_type(self, hkx_types: HKXTypeList) -> HKXType:
        return hkx_types[self.type_index]

    def get_type_name(self, hkx_types: HKXTypeList) -> str:
        return hkx_types[self.type_index].name

    def get_base_type(self, hkx_types: HKXTypeList) -> HKXType:
        return hkx_types[self.type_index].get_base_type(hkx_types)

    def get_base_type_name(self, hkx_types: HKXTypeList) -> str:
        return hkx_types[self.type_index].get_base_type(hkx_types).name

    def get_type_hierarchy(self, hkx_types: HKXTypeList) -> list[HKXType]:
        return hkx_types[self.type_index].get_type_hierarchy(hkx_types)

    def get_member_names(self, hkx_types: HKXTypeList, all_members=False) -> list[str]:
        """Get member names in proper order."""
        if all_members:
            return [m.name for m in self.get_type(hkx_types).get_all_members(hkx_types)]
        return [m.name for m in self.get_type(hkx_types).members]

    def reindex_type(self, old_hkx_types: HKXTypeList, new_hkx_types: HKXTypeList):
        node_type = old_hkx_types[self.type_index]
        self.type_index = new_hkx_types.get_type_index(node_type)

    def __repr__(self):
        return f"Node({type(self.value)})"

    def get_tree_string(self, hkx_types: HKXTypeList, object_ids: dict[HKXNode, int] = None, indent=0) -> str:
        """Recursively construct node hierarchy string (with indents), with this as the root.

        Objects that inherit from "hkBaseObject" will be given an ID, and referred to later on with that ID if they
        reappear in the tree.
        """
        ind = " " * indent
        hkx_type = hkx_types[self.type_index]  # type: HKXType
        if object_ids is None:
            object_ids = {self: 1}
        if hkx_type.get_type_hierarchy(hkx_types)[0].name_without_colons == "hkBaseObject":
            if self in object_ids:
                return f"<OBJECT {object_ids[self]}>"
            object_id = str(object_ids.setdefault(self, len(object_ids) + 1))
            lines = [f"NEW OBJECT {object_id} <{hkx_type.name_without_colons}>"]
        else:
            if hkx_type.pointer_type_index:
                pointer_name = hkx_types[hkx_type.pointer_type_index].name_without_colons
                lines = [f"<{hkx_type.name_without_colons}[{pointer_name}]>"]
            else:
                lines = [f"<{hkx_type.name_without_colons}>"]
        if isinstance(self.value, dict):
            # member_offsets = {m.name: m.byte_offset for m in hkx_type.all_members}
            lines.append("  {")
            for name in self.get_member_names(hkx_types, all_members=True):
                node = self.value[name]
                lines.append(f"    {repr(name)}: {node.get_tree_string(hkx_types, object_ids, indent + 4)}")
                # lines.append(
                #     f"    {repr(name)} ({member_offsets[name]}): {node.get_tree_string(indent + 4, object_ids)}"
                # )
            lines.append("  }")
        elif isinstance(self.value, (list, tuple)):
            o, c = ("[", "]") if isinstance(self.value, list) else ("(", ")")
            if not self.value:
                lines[-1] += f" {o}{c}"
            elif len(self.value) > 200:
                lines.append(f"  {o}<{len(self.value)} elements>{c}")
            else:
                if isinstance(self, (HKXArrayNode, HKXTupleNode)):
                    lines.append(f"  {repr(self.value)}")
                else:
                    lines.append(f"  {o}")
                    for node in self.value:
                        lines.append(f"    {node.get_tree_string(hkx_types, object_ids, indent + 4)}")
                    lines.append(f"  {c}")
        elif isinstance(self.value, HKXNode):
            lines[-1] += f" -> {self.value.get_tree_string(hkx_types, object_ids, indent + 4)}"
        else:
            lines[-1] += f" = {repr(self.value)}"
        return f"\n{ind}".join(lines)


class HKXArrayNode(HKXNode):
    SUBCLASS = "ARRAY"

    type_index: HKXType
    value: list[tp.Union[bool, int, float], ...]


class HKXTupleNode(HKXNode):
    SUBCLASS = "TUPLE"

    type_index: HKXType
    value: tuple[tp.Union[bool, int, float], ...]


class NodeCollector:
    """Build a list of all nodes starting at the given `root_node`, so nodes can be checked and modified."""

    _DEBUG_PRINT = False

    def __init__(self, root_node: HKXNode, hkx_types: HKXTypeList = None):
        self.nodes = []
        self._hkx_types = hkx_types
        self._scan_node(root_node, indent=0)

    def _scan_node(self, node: HKXNode, indent: int):
        if node in self.nodes:
            return

        self.nodes.append(node)
        if self._DEBUG_PRINT:
            debug_node_repr = node.get_type_name(self._hkx_types) if self._hkx_types else node.type_index
            print(f"{' ' * indent}Collected: {debug_node_repr}")

        if isinstance(node, (HKXArrayNode, HKXTupleNode)):
            return  # simplified subclasses don't need further collection

        if isinstance(node.value, (list, tuple)):
            for n in node.value:
                self._scan_node(n, indent=indent + 4)
        elif isinstance(node.value, dict):
            for n in node.value.values():
                self._scan_node(n, indent=indent + 4)
        elif isinstance(node.value, HKXNode):
            self._scan_node(node.value, indent=indent + 4)


class NodeFinder:

    _DEBUG_PRINT = False

    def __init__(self, name_to_find: str, root_node: HKXNode, hkx_types: HKXTypeList = None):
        self.nodes = []
        self.node_sequences = []  # type: list[list[str]]
        self._current_sequence = []  # type: list[str]
        self._name_to_find = name_to_find
        self._hkx_types = hkx_types
        self._scan_node(root_node, indent=0)

    def _scan_node(self, node: HKXNode, indent: int):
        if node in self.nodes:
            return

        self.nodes.append(node)

        if node.get_type_name(self._hkx_types) == self._name_to_find:
            self.node_sequences.append(list(self._current_sequence))

        if isinstance(node, (HKXArrayNode, HKXTupleNode)):
            return  # simplified subclasses don't need further collection

        if isinstance(node.value, (list, tuple)):
            for n in node.value:
                self._current_sequence.append(n.get_type(self._hkx_types).name_without_colons)
                self._scan_node(n, indent=indent + 4)
                self._current_sequence.pop()
        elif isinstance(node.value, dict):
            for k, n in node.value.items():
                if k == "variant":  # TODO
                    self._current_sequence.append(f"{k}<hkRefVariant>")
                else:
                    self._current_sequence.append(f"{k}<{n.get_type(self._hkx_types).name_without_colons}>")
                self._scan_node(n, indent=indent + 4)
                self._current_sequence.pop()
        elif isinstance(node.value, HKXNode):
            self._current_sequence.append(node.value.get_type(self._hkx_types).name_without_colons)
            self._scan_node(node.value, indent=indent + 4)
            self._current_sequence.pop()


class NodeTypeReindexer:
    """Dereferences all types inside node tree, generates a new HKX type list containing only the present types, then
    re-references all types to that new (smaller or equally sized) list.

    The new types will be deep-copied, so all the `HKXType` instances inside the original list should be untouched.
    """

    _DEBUG_PRINT = False
    _IGNORE_REPEAT_NAMES = False

    def __init__(self, hkx_types: HKXTypeList, root_node: HKXNode = None, new_types: HKXTypeList = None):
        self._old_types = hkx_types
        self._root_node = root_node
        self._adder_sources = {}  # type: dict[HKXType, str]

        if root_node is not None:
            if new_types is not None:
                raise ValueError("Use `root_node` to find types or supply `new_types` manually, but not both.")
            self._new_types = HKXTypeList([])
            self._added_type_names = set()
            self._scan_node_queue(deque([root_node]), add_char=True)
        else:
            if not new_types:
                raise ValueError("No `root_node` or `new_types` supplied to reindexer.")
            self._new_types = new_types

    def reindex(self) -> HKXTypeList:
        """Return a remapped copy of all found types."""

        remapped_types = copy.deepcopy(self._new_types)
        for hkx_type in remapped_types:
            hkx_type.reindex(self._old_types, self._new_types)

        self._reindexed_nodes = []
        if self._root_node:
            self._reindex_node_type(self._root_node)

        self._old_types = remapped_types  # in case you try to `remap` again accidentally
        return remapped_types

    def _scan_node_queue(self, node_queue: deque[HKXNode], indent=0, add_char=False):

        new_queue = deque()

        while node_queue:
            node = node_queue.popleft()
            self._scan_node(node, node_queue=new_queue, indent=indent)

        if add_char:
            try:
                self._add_type(self._old_types["char"])
                self._adder_sources[self._old_types["char"]] = "<char>"
            except KeyError:
                _LOGGER.warning("Could not find 'char' type in old HKX types when re-indexing. This is unusual!")

        if new_queue:
            self._scan_node_queue(new_queue, indent=indent + 4)

    def _scan_node(self, node: HKXNode, node_queue: deque[HKXNode], indent=0):
        if node is None:
            return

        node_type = node.get_type(self._old_types)
        node_base_type = node.get_base_type(self._old_types)

        self._scan_type_queue(deque([node_type]), indent=indent)

        if isinstance(node, (HKXArrayNode, HKXTupleNode)):
            return  # no further nodes to recur on

        if node_base_type.tag_data_type == TagDataType.Pointer:
            node_queue.append(node.value)
        elif node_base_type.tag_data_type == TagDataType.Class:
            for member in node_type.get_all_members(self._old_types):
                node_queue.append(node.value[member.name])
        elif node_base_type.tag_data_type & 0xF == TagDataType.Array:
            for element_node in node.value:
                node_queue.append(element_node)

    def _add_type(self, hkx_type: HKXType, indent=0):
        if hkx_type in self._new_types:
            raise ValueError(f"Type {hkx_type.name} is already in scanned type list.")
        if self._DEBUG_PRINT and (not self._IGNORE_REPEAT_NAMES or hkx_type.name not in self._added_type_names):
            print(f"{' ' * indent}    Added type: {hkx_type.name_without_colons}")
        self._new_types.append(hkx_type)
        self._added_type_names.add(hkx_type.name)

    def _scan_type_queue(self, type_queue: deque[HKXType], indent=0):

        new_queue = deque()

        while type_queue:
            hkx_type = type_queue.popleft()
            self._scan_type(hkx_type, type_queue=new_queue, indent=indent + 4)

        if new_queue:
            self._scan_type_queue(new_queue, indent=indent + 4)

    def _scan_type(self, hkx_type: HKXType, type_queue: deque[HKXType], indent=0):
        """Scan `HKXType`'s references for more `HKXType`s."""

        ind = " " * indent
        # print(f"{ind}Scanning type: {hkx_type.name}")

        if hkx_type not in self._new_types:
            self._add_type(hkx_type, indent=indent)
            self._adder_sources[hkx_type] = f"<scanned {hkx_type.name_without_colons}>"

        parent_type = hkx_type.get_parent_type(self._old_types)
        if parent_type and parent_type not in self._new_types:
            if self._DEBUG_PRINT:
                print(f"{ind} Parent:")
            self._add_type(parent_type, indent=indent)
            self._adder_sources[parent_type] = f"<parent of {hkx_type.name_without_colons}>"
            type_queue.append(parent_type)

        for template in hkx_type.templates:
            if template.name[0] == "t":
                template_type = template.get_type(self._old_types)
                if template_type and template_type not in self._new_types:
                    if self._DEBUG_PRINT:
                        print(f"{ind} Template:")
                    self._add_type(template_type, indent=indent)
                    self._adder_sources[template_type] = f"<template of {hkx_type.name_without_colons}>"
                    type_queue.append(template_type)

        pointer_type = hkx_type.get_pointer_type(self._old_types)
        if pointer_type and pointer_type not in self._new_types:
            if self._DEBUG_PRINT:
                print(f"{ind} Pointer:")
            self._add_type(pointer_type, indent=indent)
            self._adder_sources[pointer_type] = f"<pointer of {hkx_type.name_without_colons}>"
            type_queue.append(pointer_type)

        for member in hkx_type.members:
            member_type = member.get_type(self._old_types)
            if member_type and member_type in self._new_types:
                if self._DEBUG_PRINT:
                    print(
                        f"{ind} Member {member.name} type {member_type.name} already added: "
                        f"{self._adder_sources[member_type]}"
                    )
            if member_type and member_type not in self._new_types:
                if self._DEBUG_PRINT:
                    print(f"{ind} Member: {member.name}")
                self._add_type(member_type, indent=indent)
                self._adder_sources[member_type] = f"<member {member.name} of {hkx_type.name_without_colons}>"
                type_queue.append(member_type)

        for interface in hkx_type.interfaces:
            interface_type = interface.get_type(self._old_types)
            if interface_type and interface_type not in self._new_types:
                if self._DEBUG_PRINT:
                    print(f"{ind} {Fore.YELLOW}Interface:{Fore.RESET}")
                self._add_type(interface_type, indent=indent)
                self._adder_sources[interface_type] = f"<interface of {hkx_type.name_without_colons}>"
                type_queue.append(interface_type)

    def _reindex_node_type(self, node: HKXNode, indent=0):
        if node is None or node in self._reindexed_nodes:
            return

        node_type = node.get_type(self._old_types)
        node_base_type = node.get_base_type(self._old_types)

        ind = " " * indent
        if self._DEBUG_PRINT:
            print(f"{ind}Reindexing: {node_type.name} | {node_base_type.name}")
        node.reindex_type(self._old_types, self._new_types)
        self._reindexed_nodes.append(node)

        if isinstance(node, (HKXArrayNode, HKXTupleNode)):
            return  # no further nodes to recur on

        if node_base_type.tag_data_type == TagDataType.Pointer:
            if self._DEBUG_PRINT:
                print(f"{ind}  Pointer:")
            self._reindex_node_type(node.value, indent=indent + 4)
        elif node_base_type.tag_data_type == TagDataType.Class:
            for member in node_type.get_all_members(self._old_types):
                if self._DEBUG_PRINT:
                    print(f"{ind}  Member \"{member.name}\":")
                self._reindex_node_type(node.value[member.name], indent=indent + 4)
        elif node_base_type.tag_data_type & 0xF == TagDataType.Array:
            if self._DEBUG_PRINT:
                print(f"{ind}  Array:")
            for i, element_node in enumerate(node.value):
                self._reindex_node_type(element_node, indent=indent + 4)


class NodeTypeReassigner:
    """Iterates through nodes with types from list `old_types` and assigns them types from list `new_types`.

    I think this is a superior way to convert HKX instances between versions than trying to modify the type list itself.
    We just need to check at the end that EVERY node's type has changed.
    """

    _DEBUG_PRINT = False

    def __init__(self, old_types: HKXTypeList, new_types: HKXTypeList):
        self._old = old_types
        self._new = new_types
        self._reassigned = []

    def reassign_hkx(self, hkx: HKX):
        self._old_nodes = hkx.all_nodes
        self._reassigned = []
        self._discarded = []

        self._reassign_class(hkx.root, indent=0)

        for discarded_node in self._discarded:
            for discarded_child in NodeCollector(discarded_node, hkx.hkx_types).nodes:
                if discarded_child in self._old_nodes:
                    self._old_nodes.remove(discarded_child)

        # Confirm all nodes were reassigned.
        if self._old_nodes:
            missed_names = [n.get_type_name(hkx.hkx_types) for n in self._old_nodes]
            _LOGGER.error(
                f"{len(self._reassigned)} nodes reassigned and {len(self._discarded)} discarded, "
                f"but {len(missed_names)} nodes missed: {missed_names}"
            )
            raise AssertionError("Not all nodes were reassigned. See list above.")

        hkx.hkx_types = self._new  # TODO: Maybe a sneaky place to do this huge, permanent change.
        hkx.all_nodes = self._reassigned
        # hkx.collect_nodes()  # nodes themselves are untouched, no need to recollect here

    def _reassign_class(self, node: HKXNode, indent: int):
        if node in self._reassigned:
            return  # class node already appeared elsewhere (completely possible)

        old_type = node.get_type(self._old)
        old_base_type = old_type.get_base_type(self._old)
        if old_base_type.tag_data_type not in {TagDataType.Class, TagDataType.Float}:
            raise TypeError(f"Expected a Class node (or <32-bit Float node), not {old_base_type.tag_data_type.name}.")
        if not isinstance(node.value, dict):
            raise TypeError(f"Expected Class node value to be a dict, not: {node.value}")

        try:
            new_class_type = self._new[old_type.name]
        except KeyError:
            raise KeyError(f"Could not get non-generic old type {old_type.name} from new types.")

        node.type_index = self._new.get_type_index(new_class_type)
        self._reassigned.append(node)
        self._old_nodes.remove(node)
        ind = " " * indent
        if self._DEBUG_PRINT:
            print(f"{ind}Class node: {old_type.name} -> {new_class_type.name}")

        old_dict = node.value  # type: dict[str, HKXNode]
        node.value = {}
        for new_member in new_class_type.get_all_members(self._new):
            new_member_type = new_member.get_type(self._new)
            base_member_type = new_member_type.get_base_type(self._new)
            if new_member.name not in old_dict:
                # Create new default member node.
                new_type_index = self._new.get_type_index(new_member_type)
                if base_member_type.tag_data_type == TagDataType.Array:
                    if base_member_type.get_pointer_base_type(self._new).tag_data_type in {
                        TagDataType.Bool, TagDataType.Int, TagDataType.Float
                    }:
                        node.value[new_member.name] = new_node = HKXArrayNode([], new_type_index)
                    else:
                        node.value[new_member.name] = new_node = HKXNode([], new_type_index)
                elif base_member_type.tag_data_type == TagDataType.Int:
                    node.value[new_member.name] = new_node = HKXNode(0, new_type_index)
                elif base_member_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
                    node.value[new_member.name] = new_node = HKXNode(0.0, new_type_index)
                elif base_member_type.tag_data_type == TagDataType.Bool:
                    node.value[new_member.name] = new_node = HKXNode(False, new_type_index)
                elif base_member_type.tag_data_type == TagDataType.Tuple:
                    if base_member_type.get_pointer_base_type(self._new).tag_data_type in {
                        TagDataType.Bool, TagDataType.Int, TagDataType.Float
                    }:
                        node.value[new_member.name] = new_node = HKXTupleNode((), new_type_index)
                    else:
                        node.value[new_member.name] = new_node = HKXNode((), new_type_index)
                else:
                    raise TypeError(
                        f"Cannot guess default value for new member with type {new_member_type.tag_data_type.name}."
                    )
                if self._DEBUG_PRINT:
                    print(f"{ind}  Created new member: {new_member.name} ({new_node.value})")
                self._reassigned.append(new_node)

            else:
                # Use existing member and modify its type if appropriate.
                existing_member_node = old_dict.pop(new_member.name)
                if self._DEBUG_PRINT:
                    print(f"{ind}  Updating member: {new_member.name} (type {new_member_type.name})")

                if base_member_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
                    self._reassign_float(existing_member_node, new_member_type, indent=indent + 4)
                elif base_member_type.tag_data_type == TagDataType.Int:
                    self._reassign_int(existing_member_node, new_member_type, indent=indent + 4)
                elif base_member_type.tag_data_type == TagDataType.Bool:
                    self._reassign_bool(existing_member_node, new_member_type, indent=indent + 4)
                elif base_member_type.tag_data_type == TagDataType.String:
                    self._reassign_string(existing_member_node, indent=indent + 4)
                elif base_member_type.tag_data_type == TagDataType.Array:
                    self._reassign_array(existing_member_node, new_member_type, indent=indent + 4)
                elif base_member_type.tag_data_type == TagDataType.Tuple:
                    self._reassign_tuple(existing_member_node, new_member_type, indent=indent + 4)
                elif base_member_type.tag_data_type in {TagDataType.Class, TagDataType.Float}:
                    self._reassign_class(existing_member_node, indent=indent + 4)
                elif base_member_type.tag_data_type == TagDataType.Pointer:
                    self._reassign_pointer(existing_member_node, new_member_type, indent=indent + 4)
                else:
                    raise TypeError(
                        f"Cannot process member (\"{new_member.name}\" of {old_type.name}) type: {new_member_type.name}"
                        f" with data type {base_member_type.tag_data_type.name}."
                    )

                node.value[new_member.name] = existing_member_node

        for deprecated_member_name, deprecated_node in old_dict.items():
            # Deprecated or renamed members. Removed from old list so we don't expect them to be reassigned.
            # Child nodes will be removed later using `_discarded`, once we can confirm they weren't removed somewhere
            # else already.
            self._old_nodes.remove(deprecated_node)
            self._discarded.append(deprecated_node)
            if self._DEBUG_PRINT:
                print(f"{ind}  Discarding deprecated member: {deprecated_member_name}")

    def _reassign_array(self, node: HKXNode, new_array_type: HKXType, indent: int):
        if not isinstance(node.value, list):
            raise TypeError(f"Expected Array node value to be a list, not: {node.value}")

        ind = " " * indent

        if node in self._reassigned:
            return  # already done (array appeared somewhere else)
        node.type_index = self._new.get_type_index(new_array_type)
        self._reassigned.append(node)
        self._old_nodes.remove(node)
        if self._DEBUG_PRINT:
            print(
                f"{ind}Array: {new_array_type.name} ({new_array_type.get_pointer_base_type(self._new).name}) "
                f"({len(node.value)} elements)"
            )

        if isinstance(node, HKXArrayNode):
            # No elements to recur on.
            if self._DEBUG_PRINT:
                print(f"{ind}*Simple Array Node*")
            return

        array_element_type = new_array_type.get_pointer_type(self._new)
        array_element_base_type = array_element_type.get_base_type(self._new)

        if array_element_base_type.tag_data_type == TagDataType.Array:
            # I don't think this has ever happened (array of arrays) but no reason it couldn't.
            for element_node in node.value:
                self._reassign_array(element_node, array_element_type, indent=indent + 4)
        elif array_element_base_type.tag_data_type == TagDataType.Tuple:
            for element_node in node.value:
                self._reassign_tuple(element_node, array_element_type, indent=indent + 4)
        elif array_element_base_type.tag_data_type == TagDataType.Class:
            for element_node in node.value:
                self._reassign_class(element_node, indent=indent + 4)
        elif array_element_base_type.tag_data_type == TagDataType.Pointer:
            for element_node in node.value:
                self._reassign_pointer(element_node, array_element_type, indent=indent + 4)
        elif array_element_base_type.tag_data_type == TagDataType.String:
            for element_node in node.value:
                self._reassign_string(element_node, indent=indent + 4)
        elif array_element_base_type.tag_data_type == TagDataType.Bool:
            for element_node in node.value:
                self._reassign_bool(element_node, array_element_type, indent=indent + 4)
        elif array_element_base_type.tag_data_type == TagDataType.Int:
            for element_node in node.value:
                self._reassign_int(element_node, array_element_type, indent=indent + 4)
        elif array_element_base_type.tag_data_type == TagDataType.Float:
            for element_node in node.value:
                self._reassign_float(element_node, array_element_type, indent=indent + 4)
        elif array_element_base_type.tag_data_type == TagDataType.Invalid:
            if array_element_base_type.name_without_colons != "hkReflectDetailOpaque":
                # Only one "Invalid" type has been observed. Nothing to recur on.
                _LOGGER.warning(f"Encountered unexpected Invalid node type: {array_element_base_type.name}")
        else:
            raise TypeError(
                f"Cannot process array element type: {array_element_type.name} "
                f"({array_element_base_type.tag_data_type.name})"
            )

    def _reassign_tuple(self, node: HKXNode, new_tuple_type: HKXType, indent: int):
        if not isinstance(node.value, tuple):
            raise TypeError(f"Expected Tuple node value to be a tuple, not: {node.value}")

        if node in self._reassigned:
            return  # already done (tuple appeared somewhere else)
        node.type_index = self._new.get_type_index(new_tuple_type)
        self._reassigned.append(node)
        self._old_nodes.remove(node)
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}Tuple: {new_tuple_type.name}")

        if isinstance(node, HKXTupleNode):
            # No elements to recur on.
            return

        base_tuple_type = new_tuple_type.get_base_type(self._new)
        tuple_element_type = base_tuple_type.get_pointer_type(self._new)
        base_element_type = tuple_element_type.get_base_type(self._new)

        if tuple_element_type.tag_data_type == TagDataType.Array:
            for element_node in node.value:
                self._reassign_array(element_node, tuple_element_type, indent=indent + 4)
        elif tuple_element_type.tag_data_type == TagDataType.Class:
            for element_node in node.value:
                self._reassign_class(element_node, indent=indent + 4)
        elif tuple_element_type.tag_data_type == TagDataType.Pointer:
            for element_node in node.value:
                self._reassign_pointer(element_node, tuple_element_type, indent=indent + 4)
        elif tuple_element_type.tag_data_type == TagDataType.String:
            for element_node in node.value:
                self._reassign_string(element_node, indent=indent + 4)
        elif base_element_type.tag_data_type == TagDataType.Tuple:
            for element_node in node.value:
                self._reassign_tuple(element_node, tuple_element_type, indent=indent + 4)
        elif base_element_type.tag_data_type == TagDataType.Bool:
            for element_node in node.value:
                self._reassign_bool(element_node, tuple_element_type, indent=indent + 4)
        elif base_element_type.tag_data_type == TagDataType.Int:
            for element_node in node.value:
                self._reassign_int(element_node, tuple_element_type, indent=indent + 4)
        elif base_element_type.tag_data_type == TagDataType.Float:
            for element_node in node.value:
                self._reassign_float(element_node, tuple_element_type, indent=indent + 4)
        else:
            raise TypeError(f"Cannot process tuple element type: {tuple_element_type.name}")

    def _reassign_pointer(self, node: HKXNode, new_pointer_type: HKXType, indent: int):
        """This includes `hkRefVariant` and `hkRefPtr` types - though these technically have "ptr" members, those are
        not visible in the node, which acts like a normal pointer.
        """
        if node.value is not None and not isinstance(node.value, HKXNode):
            raise TypeError(f"Expected Pointer node value to be another node (or `None`), not: {node.value}")

        if node in self._reassigned:
            print("ALREADY REASSIGNED")
            return  # already done (pointer appeared somewhere else)
        node.type_index = self._new.get_type_index(new_pointer_type)
        self._reassigned.append(node)
        self._old_nodes.remove(node)
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}Pointer: {new_pointer_type.name}")

        if node.value is None:
            return

        reference_type = new_pointer_type.get_pointer_type(self._new)
        reference_base_type = reference_type.get_base_type(self._new)

        if reference_base_type.tag_data_type == TagDataType.Array:
            self._reassign_array(node.value, reference_type, indent=indent + 4)
        elif reference_base_type.tag_data_type == TagDataType.Class:
            self._reassign_class(node.value, indent=indent + 4)
        elif reference_base_type.tag_data_type == TagDataType.Pointer:
            self._reassign_pointer(node.value, reference_type, indent=indent + 4)
        # Pointer reference types can't be primitives.
        else:
            raise TypeError(f"Cannot process pointer reference type: {reference_type.name}")

    def _reassign_string(self, node: HKXNode, indent: int):
        """Strings can be `None`, if the pointer was absent while unpacking."""
        if node.value is not None and not isinstance(node.value, str):
            raise TypeError(f"Expected String node value to be a string (or `None`), not: {node.value}")

        if node in self._reassigned:
            return  # already done (string appeared somewhere else, though I think this is unlikely)
        node.type_index = self._new.get_type_index("hkStringPtr")
        self._reassigned.append(node)
        self._old_nodes.remove(node)
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}String")

    def _reassign_bool(self, node: HKXNode, new_bool_type: HKXType, indent: int):
        """Bool type should always be `hkBool`."""
        if not isinstance(node.value, bool):
            raise TypeError(f"Expected Bool node value to be a bool, not: {node.value}")

        if new_bool_type is not self._new["hkBool"]:
            raise AssertionError(f"Expected new bool type to be 'hkBool', not: {new_bool_type.name}")

        if node in self._reassigned:
            return  # already done (bool appeared somewhere else, though I think this is impossible)
        node.type_index = self._new.get_type_index(new_bool_type)
        self._reassigned.append(node)
        self._old_nodes.remove(node)
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}Bool: {new_bool_type.name}")

    def _reassign_int(self, node: HKXNode, new_int_type: HKXType, indent: int):
        if not isinstance(node.value, int):
            raise TypeError(f"Expected Int node value to be a bool, not: {node.value}")

        if node in self._reassigned:
            return  # already done (int appeared somewhere else, though I think this is impossible)
        node.type_index = self._new.get_type_index(new_int_type)
        self._reassigned.append(node)
        self._old_nodes.remove(node)
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}Int: {new_int_type.name}")

    def _reassign_float(self, node: HKXNode, new_float_type: HKXType, indent: int):
        if not isinstance(node.value, float):
            raise TypeError(f"Expected Float node value to be a float, not: {node.value} ({type(node.value)})")

        if node in self._reassigned:
            return  # already done (float appeared somewhere else, though I think this is impossible)
        node.type_index = self._new.get_type_index(new_float_type)
        self._reassigned.append(node)
        self._old_nodes.remove(node)
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}Float: {new_float_type.name}")


class NodeComparer:

    _PRINT_ALL = False
    _PRINT_DIFFS = True
    _PRINT_STACK_SIZE = 3

    # Pairs of (type_name, member_name) to not step into (known to be too large/always different).
    _SKIP = (
        # ("hkaSplineCompressedAnimation", "data"),
    )

    def __init__(self, hkx_1: HKX, hkx_2: HKX):
        self._hkx_1 = hkx_1
        self._hkx_2 = hkx_2

    def compare(self, float_precision=5, take_close_floats_from_hkx_2=False, take_changes_from_hkx_2=False):
        """Check if all nodes' values are equal (at the bottom level)."""
        self._size_change_count = 0
        self._difference_count = 0
        self._close_float_count = 0
        self._prec = float_precision
        self._take_close_floats = take_close_floats_from_hkx_2
        self._take_changes = take_changes_from_hkx_2
        self._types_1 = self._hkx_1.hkx_types
        self._types_2 = self._hkx_2.hkx_types
        self._compared_nodes = []
        self._check_node(self._hkx_1.root, self._hkx_2.root, type_stack=[])
        if self._PRINT_ALL or self._PRINT_DIFFS:
            print(
                f"Full node comparison raised zero type errors, {Fore.RED}{self._size_change_count} size errors"
                f"{Fore.RESET}, {Fore.YELLOW}{self._close_float_count} floats within precision range{Fore.RESET}, and "
                f"{Fore.RED}{self._difference_count} differences{Fore.RESET}."
            )
            if self._take_changes:
                print(f"All differences were removed by setting node values in HKX 1 to those in HKX 2.")
            elif self._take_close_floats:
                print(f"All tolerated float precision errors were fixed by setting node values in HKX 1 to HKX 2.")

    def _check_node(self, node_1: HKXNode, node_2: HKXNode, type_stack: list[str], indent=0, do_not_recur=False):
        ind = " " * indent
        if self._PRINT_ALL:
            print(f"{ind}{node_1.get_type_name(self._types_1)} vs. {node_2.get_type_name(self._types_2)}")

        if node_1 in self._compared_nodes:
            if self._PRINT_ALL:
                print(f"{ind}{Fore.GREEN}ALREADY COMPARED{Fore.RESET}")
            return
        self._compared_nodes.append(node_1)

        if isinstance(node_1.value, list):
            if not isinstance(node_2.value, list):
                print(
                    f"{ind}Node 1 ({node_1.type_index}) is a list, "
                    f"Node 2 ({node_2.type_index}) is a {type(node_2.value)}."
                )
                raise TypeError
            if len(node_1.value) != len(node_2.value):
                self._size_change_count += 1
                if self._PRINT_ALL or self._PRINT_DIFFS:
                    print(
                        f"{ind}{Fore.RED}List Node 1 ({len(node_1.value)}) has a different size to "
                        f"Node 2 ({len(node_2.value)}).{Fore.RESET}"
                    )
            if isinstance(node_1, HKXArrayNode):
                if not isinstance(node_2, HKXArrayNode):
                    print(f"Node 1 type: {node_1.get_type_name(self._hkx_1.hkx_types)}")
                    print(f"Node 1 value: {node_1.value}")
                    print(f"Node 2 type: {node_2.get_type_name(self._hkx_2.hkx_types)}")
                    print(f"Node 2 value: {node_2.value}")
                    raise TypeError(f"List node 1 was a `HKXArrayNode`, but list node 2 was not.")
                pass  # don't recur on simple array nodes
            elif isinstance(node_2, HKXArrayNode):
                print(f"Node 1 type: {node_1.get_type_name(self._hkx_1.hkx_types)}")
                print(f"Node 1 value: {node_1.value}")
                print(f"Node 2 type: {node_2.get_type_name(self._hkx_2.hkx_types)}")
                print(f"Node 2 value: {node_2.value}")
                raise TypeError(f"List node 2 was a `HKXArrayNode`, but list node 1 was not.")
            elif not do_not_recur:
                for n1, n2 in zip(node_1.value, node_2.value):
                    type_stack.append(node_1.get_type_name(self._hkx_1.hkx_types))
                    self._check_node(n1, n2, type_stack, indent=indent + 4)
                    type_stack.pop()
            else:
                if self._PRINT_ALL or self._PRINT_DIFFS:
                    print(
                        f"{ind}{Fore.MAGENTA}SKIPPED "
                        f"(array element type {self._hkx_1.hkx_types[node_1.value[0].type_index].name}){Fore.RESET}"
                    )

        elif isinstance(node_1.value, tuple):
            if not isinstance(node_2.value, tuple):
                print(f"{ind}Node 1 ({node_1.type_index}) is a tuple, Node 2 ({node_2.type_index}) is not.")
                raise TypeError
            if len(node_1.value) != len(node_2.value):
                self._size_change_count += 1
                if self._PRINT_ALL or self._PRINT_DIFFS:
                    print(
                        f"{ind}{Fore.RED}Tuple Node 1 ({len(node_1.value)}) has a different size to "
                        f"Node 2 ({len(node_2.value)}).{Fore.RESET}"
                    )
            if isinstance(node_1, HKXTupleNode):
                if not isinstance(node_2, HKXTupleNode):
                    raise TypeError(f"Tuple node 1 was a `HKXArrayNode`, but tuple node 2 was not.")
                pass  # don't recur on simple tuple nodes
            elif isinstance(node_2, HKXTupleNode):
                raise TypeError(f"Tuple node 2 was a `HKXArrayNode`, but tuple node 1 was not.")
            elif not do_not_recur:
                for n1, n2 in zip(node_1.value, node_2.value):
                    type_stack.append(node_1.get_type_name(self._hkx_1.hkx_types))
                    self._check_node(n1, n2, type_stack, indent=indent + 4)
                    type_stack.pop()
            else:
                if self._PRINT_ALL:
                    print(f"{ind}{Fore.MAGENTA}SKIPPED{Fore.RESET}")

        elif isinstance(node_1.value, dict):
            if not isinstance(node_2.value, dict):
                print(f"{ind}Node 1 ({node_1.type_index}) is a dict, Node 2 ({node_2.type_index}) is not.")
                raise TypeError
            if sorted(node_1.value.keys()) != sorted(node_2.value.keys()):
                print(f"{ind}Node 1 ({node_1.type_index}) has different members to Node 2 ({node_2.type_index}).")
                raise TypeError
            node_1_type = self._types_1[node_1.type_index]
            for member_name in [m.name for m in node_1_type.get_all_members(self._types_1)]:
                if self._PRINT_ALL:
                    print(f"{ind}  {Fore.CYAN}Member: \"{member_name}\"{Fore.RESET}")
                type_stack.append(node_1.get_type_name(self._hkx_1.hkx_types) + f"[{member_name}]")
                self._check_node(
                    node_1.value[member_name],
                    node_2.value[member_name],
                    type_stack,
                    indent=indent + 4,
                    do_not_recur=(node_1_type.name, member_name) in self._SKIP,
                )
                type_stack.pop()

        elif isinstance(node_1.value, HKXNode):
            if not isinstance(node_2.value, HKXNode):
                print(f"{ind}Node 1 ({node_1.type_index}) is a node, Node 2 ({node_2.type_index}) is not.")
                raise TypeError
            if not do_not_recur:
                type_stack.append(node_1.get_type_name(self._hkx_1.hkx_types))
                self._check_node(node_1.value, node_2.value, type_stack, indent=indent + 4)
                type_stack.pop()
            else:
                if self._PRINT_ALL:
                    print(f"{ind}{Fore.MAGENTA}SKIPPED{Fore.RESET}")

        elif isinstance(node_1.value, int):
            if not isinstance(node_2.value, int):
                print(f"{ind}Node 1 ({node_1.type_index}) is an integer, Node 2 ({node_2.type_index}) is not.")
                raise TypeError
            if node_1.value != node_2.value:
                self._difference_count += 1
                if self._take_changes:
                    if self._PRINT_ALL or self._PRINT_DIFFS:
                        if self._PRINT_DIFFS:
                            print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                        print(f"{ind}  {Fore.RED}{node_1.value} <- {node_2.value}{Fore.RESET}")
                    node_1.value = node_2.value
                else:
                    if self._PRINT_ALL or self._PRINT_DIFFS:
                        if self._PRINT_DIFFS:
                            print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                        print(f"{ind}  {Fore.RED}{node_1.value} != {node_2.value}{Fore.RESET}")
            else:
                if self._PRINT_ALL:
                    print(f"{ind}  == {node_1.value}")

        elif isinstance(node_1.value, str):
            if not isinstance(node_2.value, str):
                print(f"{ind}Node 1 ({node_1.type_index}) is a string, Node 2 ({node_2.type_index}) is not.")
                raise TypeError
            if node_1.value != node_2.value:
                self._difference_count += 1
                if self._take_changes:
                    if self._PRINT_ALL or self._PRINT_DIFFS:
                        if self._PRINT_DIFFS:
                            print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                        print(f"{ind}  {Fore.RED}\"{node_1.value}\" <- \"{node_2.value}\"{Fore.RESET}")
                    node_1.value = node_2.value
                else:
                    if self._PRINT_ALL or self._PRINT_DIFFS:
                        if self._PRINT_DIFFS:
                            print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                        print(f"{ind}  {Fore.RED}\"{node_1.value}\" != \"{node_2.value}\"{Fore.RESET}")
            else:
                if self._PRINT_ALL:
                    print(f"{ind}  == \"{node_1.value}\"")

        elif isinstance(node_1.value, float):
            if not isinstance(node_2.value, float):
                print(f"{ind}Node 1 ({node_1.type_index}) is a float, Node 2 ({node_2.type_index}) is not.")
                raise TypeError
            if node_1.value != node_2.value:
                if math.isclose(node_1.value, node_2.value, abs_tol=10 ** -self._prec):
                    self._close_float_count += 1
                    if self._take_close_floats:
                        node_1.value = node_2.value
                        if self._PRINT_ALL or self._PRINT_DIFFS:
                            if self._PRINT_DIFFS:
                                print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                            print(f"{ind}  {Fore.YELLOW}{node_1.value} <- {node_2.value}{Fore.RESET}")
                    else:
                        if self._take_changes:
                            if self._PRINT_ALL or self._PRINT_DIFFS:
                                if self._PRINT_DIFFS:
                                    print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                                print(f"{ind}  {Fore.RED}{node_1.value} <- {node_2.value}{Fore.RESET}")
                            node_1.value = node_2.value
                        else:
                            if self._PRINT_ALL:
                                print(f"{ind}  {Fore.YELLOW}{node_1.value} ~= {node_2.value}{Fore.RESET}")
                else:
                    self._difference_count += 1
                    if self._take_changes:
                        if self._PRINT_ALL or self._PRINT_DIFFS:
                            if self._PRINT_DIFFS:
                                print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                            print(f"{ind}  {Fore.RED}{node_1.value} <- {node_2.value}{Fore.RESET}")
                        node_1.value = node_2.value
                    else:
                        if self._PRINT_ALL or self._PRINT_DIFFS:
                            if self._PRINT_DIFFS:
                                print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                            print(f"{ind}  {Fore.RED}{node_1.value} != {node_2.value}{Fore.RESET}")
            else:
                if self._PRINT_ALL:
                    print(f"{ind}  == {node_1.value}")

        elif isinstance(node_1.value, bool):
            if not isinstance(node_2.value, bool):
                print(f"{ind}Node 1 ({node_1.type_index}) is a bool, Node 2 ({node_2.type_index}) is not.")
                raise TypeError
            if node_1.value != node_2.value:
                self._difference_count += 1
                if self._take_changes or self._PRINT_DIFFS:
                    if self._PRINT_DIFFS:
                        print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                    print(f"{ind}  {Fore.RED}{node_1.value} <- {node_2.value}{Fore.RESET}")
                    node_1.value = node_2.value
                else:
                    if self._PRINT_ALL or self._PRINT_DIFFS:
                        if self._PRINT_DIFFS:
                            print(Fore.CYAN + " > ".join(type_stack[-self._PRINT_STACK_SIZE:]) + Fore.RESET)
                        print(f"{ind}  {Fore.RED}{node_1.value} != {node_2.value}{Fore.RESET}")
            else:
                if self._PRINT_ALL:
                    print(f"{ind}  == {node_1.value}")

        elif node_1.value is None:
            if node_2.value is not None:
                print(f"{ind}Node 1 ({node_1.type_index}) is None, Node 2 ({node_2.type_index}) is not.")
                raise TypeError

        elif node_2.value is None:
            print(f"{ind}Node 2 ({node_2.type_index}) is None, Node 1 ({node_1.type_index}) is not.")
            raise TypeError

        else:
            raise TypeError(f"Unrecognized Node 1 value type: {type(node_1.value)}")
