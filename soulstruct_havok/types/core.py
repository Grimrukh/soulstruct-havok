from __future__ import annotations

__all__ = [
    "MissingTypeError",
    "DefType",
    "TemplateType",
    "TemplateValue",
    "Member",
    "Interface",
    "hk",
    "hkBasePointer",
    "hkArray_",
    "hkArray",
    "hkStruct_",
    "hkStruct",
    "hkGenericStruct",
    "hkEnum_",
    "hkEnum",
    "Ptr_",
    "Ptr",
    "hkRefPtr_",
    "hkRefPtr",
    "hkRefVariant_",
    "hkRefVariant",
    "hkViewPtr_",
    "hkViewPtr",
    "NewStruct_",
    "NewStruct",
    "pack_string",
    "unpack_named_variant",
    "unpack_named_variant_packfile",
    "pack_named_variant",
    "TypeInfoGenerator",
    "SET_DEBUG_PRINT",
]

import inspect
import sys
import typing as tp
from collections import deque
from pathlib import Path

from colorama import init as colorama_init, Fore

from soulstruct.utilities.binary import BinaryReader, BinaryWriter
from soulstruct.utilities.inspection import get_hex_repr

from soulstruct_havok.enums import TagDataType, TagMemberFlags
from soulstruct_havok.packfile.structs import PackFileItemEntry
from soulstruct_havok.tagfile.structs import TagFileItem
from soulstruct_havok.types.info import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.packfile.structs import PackFileItemEntry


# TODO: hard-coded pointer byte size/alignment is long (8 bits). They should respect some global pointer size.


colorama_init()


_DEBUG_PRINT_UNPACK = False
_DEBUG_PRINT_PACK = False
_INDENT = 0
_REQUIRE_INPUT = False


def SET_DEBUG_PRINT(unpack=False, pack=False):
    global _DEBUG_PRINT_UNPACK, _DEBUG_PRINT_PACK
    _DEBUG_PRINT_UNPACK = unpack
    _DEBUG_PRINT_PACK = pack


def _debug_print_unpack(msg: tp.Any):
    global _INDENT
    if _DEBUG_PRINT_UNPACK:
        print(" " * _INDENT + str(msg))


def _debug_print_pack(msg: tp.Any):
    global _INDENT
    if _DEBUG_PRINT_PACK:
        print(" " * _INDENT + str(msg))


def _increment_debug_indent():
    global _INDENT
    _INDENT += 4


def _decrement_debug_indent():
    global _INDENT
    _INDENT -= 4


class MissingTypeError(Exception):
    pass


class DefType:

    def __init__(self, type_name: str, action: tp.Callable[[], tp.Type[hk]]):
        """Deferred reference to own class (before Python has finished defining it).

        `action` will be used to set the attribute the first time it is accessed.
        """
        self.type_name = type_name
        self.action = action


class TemplateType(tp.NamedTuple):
    """Container for 't' templates."""
    name: str
    type: tp.Type[hk]


class TemplateValue(tp.NamedTuple):
    """Container for 'v' templates."""
    name: str
    value: int


class Member(tp.NamedTuple):
    """Simple container for member information."""
    offset: int
    name: str
    type: tp.Union[tp.Type[hk], DefType]
    flags: int = TagMemberFlags.Default


class Interface(tp.NamedTuple):
    """Container for interface information."""
    type: tp.Type[hk]
    flags: int


class hk:
    """Absolute base of every Havok type."""
    alignment = 0
    byte_size = 0
    tag_type_flags = 0

    # This field is used by tagfiles to indicate which of these other attributes should be read/written.
    __tag_format_flags = 0

    # These fields are optional (defaulting to `None`), not inherited, and readable via property.
    __hsh = None  # type: tp.Optional[int]  # not used by some types
    __abstract_value = None  # type: tp.Optional[int]  # only used by some Classes
    __version = None  # type: tp.Optional[int]  # only used by some Classes

    __real_name = ""  # if different to type name (e.g., may contain colons, spaces, or clash with a Python type)

    local_members: tuple[Member, ...] = ()  # only members added by this class
    members: tuple[Member, ...] = ()  # includes all parent class members
    # We only care about local, mangled templates/interfaces, since they are never used in unpacking.
    __templates: tuple[TemplateValue | TemplateType, ...] = ()
    __interfaces: tuple[TemplateValue | TemplateType, ...] = ()

    def __init__(self, **kwargs):
        """Instance can be initiated with member `kwargs`."""
        if kwargs:
            member_names = self.get_member_names()
            for member_name, member_value in kwargs.items():
                if member_name not in member_names:
                    raise ValueError(f"Invalid member passed to `{self.get_type_name()}`: {member_name}")
                setattr(self, member_name, member_value)

    @classmethod
    def get_type_name(cls):
        """Easier way (especially for instances) to get Python class name."""
        return cls.__name__

    @classmethod
    def get_member_names(cls):
        return [m.name for m in cls.members]

    @classmethod
    def get_type_with_member(cls, member_name: str) -> tp.Type[hk]:
        """Find the Havok type in this class's hierarchy that actually defines the given `member_name`."""
        for parent_type in cls.get_type_hierarchy():
            if member_name in [m.name for m in parent_type.local_members]:
                return parent_type
        raise ValueError(f"Member '{member_name}' is not defined by any base type of {cls.get_type_name()}.")

    @classmethod
    def get_tag_data_type(cls):
        # TODO: Testing out ignoring the first bit, because `hkStringPtr` in 2018 seems to have a 1 in its MSB but no
        #  other functional difference I can see...
        return TagDataType(cls.tag_type_flags & 0b01111111)

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-2])  # exclude `hk` and `object`

    @classmethod
    def get_immediate_parent(cls) -> tp.Optional[tp.Type[hk]]:
        """Get immediate `hk` parent if one exists."""
        hierarchy = cls.get_type_hierarchy()
        if len(hierarchy) > 1:
            return hierarchy[1]
        return None

    @classmethod
    def unpack(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> tp.Any:
        """Unpack a `hk` instance from `reader`.

        Primitive types are converted to their Python equivalent, arrays are converted to list (in their overriding
        method), and so on. The types stored in the `hk` definition indicate how these Python values should be repacked
        by `pack()` below.
        """
        reader.seek(offset)
        _debug_print_unpack(f"Unpacking `{cls.__name__}`... ({cls.get_tag_data_type().name}) <{hex(offset)}>")

        if cls.__name__ == "hkRootLevelContainerNamedVariant":
            # Retrieve other classes from subclass's module, as they will be dynamically attached to the root container.
            all_types = {
                hk_type.__name__: hk_type
                for hk_type in inspect.getmembers(
                    sys.modules[cls.__module__], lambda x: inspect.isclass(x) and issubclass(x, hk)
                )
            }
            return unpack_named_variant(cls, reader, items, all_types)

        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot unpack opaque type (and there shouldn't be anything to unpack in the file).
            value = None
        elif tag_data_type == TagDataType.Bool:
            value = unpack_bool(cls, reader)
        elif tag_data_type == TagDataType.String:
            value = unpack_string(reader, items)  # `cls` not needed
        elif tag_data_type == TagDataType.Int:
            value = unpack_int(cls, reader)
        elif cls.tag_type_flags == TagDataType.Float | TagDataType.Float32:
            value = unpack_float32(reader)  # `cls` not needed
        elif tag_data_type in {TagDataType.Class, TagDataType.Float}:  # non-32-bit floats have members
            value = unpack_class(cls, reader, items)
        else:
            # Note that 'Pointer', 'Array', and 'Struct' types have their own explicit subclasses.
            raise ValueError(f"Cannot unpack `hk` subclass `{cls.__name__}` with tag data type {tag_data_type}.")
        _debug_print_unpack(f"-> {repr(value)}")
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItemEntry, offset: int = None, pointer_size=8):
        """Unpack Python data from a Havok packfile.

        If `offset` is None, the `entry.reader` continues from its current position.

        `entry` already contains resolved pointers to other entries, so no entry list needs to be passed around.
        """
        offset = entry.reader.seek(offset) if offset is not None else entry.reader.position
        _debug_print_unpack(f"Unpacking `{cls.__name__}`... ({cls.get_tag_data_type().name}) <{hex(offset)}>")

        if cls.__name__ == "hkRootLevelContainerNamedVariant":
            # Retrieve other classes from subclass's module, as they will be dynamically attached to the root container.
            all_types = {
                hk_type.__name__: hk_type
                for hk_type in inspect.getmembers(
                    sys.modules[cls.__module__], lambda x: inspect.isclass(x) and issubclass(x, hk)
                )
            }
            return unpack_named_variant_packfile(cls, entry, pointer_size, all_types)

        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot unpack opaque type (and there shouldn't be anything to unpack in the file).
            value = None
        elif tag_data_type == TagDataType.Bool:
            value = unpack_bool(cls, entry.reader)
        elif tag_data_type == TagDataType.String:
            value = unpack_string_packfile(entry, pointer_size=pointer_size)  # `cls` not needed
        elif tag_data_type == TagDataType.Int:
            value = unpack_int(cls, entry.reader)
        elif cls.tag_type_flags == TagDataType.Float | TagDataType.Float32:
            value = unpack_float32(entry.reader)  # `cls` not needed
        elif tag_data_type in {TagDataType.Class, TagDataType.Float}:  # non-32-bit floats have members
            value = unpack_class_packfile(cls, entry, pointer_size=pointer_size)
        else:
            # Note that 'Pointer', 'Array', and 'Struct' types have their own explicit subclasses.
            raise ValueError(f"Cannot unpack `hk` subclass `{cls.__name__}` with tag data type {tag_data_type}.")
        _debug_print_unpack(f"-> {repr(value)}")
        entry.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack(
        cls,
        item: TagFileItem,
        value: tp.Any,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        """Use this `hk` type to process and pack the Python `value`.

        Primitive types and structs can be packed immediately, without creating a new item (whichever item the `writer`
        is currently in is correct). For types with members (Class types), any pointer, array, and string member types
        will cause a new item to be created with its own `BinaryWriter`; this item's data, once complete, will be stored
        in its `data` attribute, and all items' data can be assembled in order at the end.
        """
        _debug_print_pack(f"Packing `{cls.__name__}` with value {repr(value)}... ({cls.get_tag_data_type().name})")

        if cls.__name__ == "hkRootLevelContainerNamedVariant":
            return pack_named_variant(cls, item, value, items, existing_items, item_creation_queue)

        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot pack opaque type (and the file expects no data).
            pass
        elif tag_data_type == TagDataType.Bool:
            pack_bool(cls, item, value)
        elif tag_data_type == TagDataType.String:
            pack_string(cls, item, value, items, item_creation_queue)
        elif tag_data_type == TagDataType.Int:
            pack_int(cls, item, value)
        elif tag_data_type == TagDataType.Float:
            pack_float(cls, item, value)
        elif tag_data_type == TagDataType.Class:
            pack_class(cls, item, value, items, existing_items, item_creation_queue)
        else:
            # 'Pointer' and 'Array' types are handled by `Ptr_` and `hkArray_` subclasses, respectively.
            raise ValueError(f"Cannot pack `hk` subclass `{cls.__name__}` with tag data type {tag_data_type.name}.")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItemEntry,
        value: tp.Any,
        existing_items: dict[hk, PackFileItemEntry],
        data_pack_queue: dict[str, deque[tp.Callable]],
        pointer_size: int,
    ):
        """Use this `hk` type to process and pack the Python `value`.

        Primitive types and structs can be packed immediately, without creating a new item (whichever item the `writer`
        is currently in is correct). For types with members (Class types), any pointer, array, and string member types
        will cause a new item to be created with its own `BinaryWriter`; this item's data, once complete, will be stored
        in its `data` attribute, and all items' data can be assembled in order at the end.
        """
        _debug_print_pack(f"Packing `{cls.__name__}` with value {repr(value)}... ({cls.get_tag_data_type().name})")

        if cls.__name__ == "hkRootLevelContainerNamedVariant":
            return pack_named_variant_packfile(cls, item, value, existing_items, data_pack_queue, pointer_size)

        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot pack opaque type (and the file expects no data).
            pass
        elif tag_data_type == TagDataType.Bool:
            pack_bool(cls, item, value)
        elif tag_data_type == TagDataType.String:
            pack_string_packfile(item, value, data_pack_queue, pointer_size)  # `cls` not needed
        elif tag_data_type == TagDataType.Int:
            pack_int(cls, item, value)
        elif tag_data_type == TagDataType.Float:
            pack_float_packfile(cls, item, value, pointer_size)
        elif tag_data_type == TagDataType.Class:
            pack_class_packfile(cls, item, value, existing_items, data_pack_queue, pointer_size)
        else:
            # 'Pointer' and 'Array' types are handled by `Ptr_` and `hkArray_` subclasses, respectively.
            raise ValueError(f"Cannot pack `hk` subclass `{cls.__name__}` with tag data type {tag_data_type.name}.")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        """Construct a `TypeInfo` with all information except references to other `TypeInfo`s, which is done later."""
        type_info = TypeInfo(cls.get_real_name())
        type_info.py_class = cls
        if (parent_type := cls.__base__) != hk:
            type_info.parent_type_py_name = parent_type.__name__
        type_info.tag_format_flags = cls.get_tag_format_flags()
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.byte_size
        type_info.alignment = cls.alignment
        type_info.version = cls.get_version()
        type_info.abstract_value = cls.get_abstract_value()
        type_info.hsh = cls.get_hsh()

        type_info.templates = []
        for template in cls.get_templates():
            if isinstance(template, TemplateValue):
                type_info.templates.append(TemplateInfo(template.name, value=template.value))
            else:
                type_info.templates.append(TemplateInfo(template.name, type_py_name=template.type.__name__))

        type_info.members = [
            MemberInfo(member.name, member.flags, member.offset, type_py_name=member.type.__name__)
            for member in cls.local_members
        ]

        type_info.interfaces = [
            InterfaceInfo(interface.flags, type_py_name=interface.type.__name__)
            for interface in cls.get_interfaces()
        ]

        return type_info

    def __getitem__(self, member_name: str):
        if not self.members:
            raise TypeError(f"Havok type {self.__class__.__name__} has no members.")
        if member_name not in self.get_member_names():
            raise AttributeError(f"Havok type {self.__class__.__name__} has no member called '{member_name}'.")
        return getattr(self, member_name)

    @classmethod
    def get_real_name(cls) -> str:
        return getattr(cls, f"_{cls.__name__.lstrip('_')}__real_name", cls.__name__)

    @classmethod
    def get_tag_format_flags(cls) -> tp.Optional[int]:
        return getattr(cls, f"_{cls.__name__.lstrip('_')}__tag_format_flags", None)

    @classmethod
    def get_hsh(cls) -> tp.Optional[int]:
        return getattr(cls, f"_{cls.__name__.lstrip('_')}__hsh", None)

    @classmethod
    def get_abstract_value(cls) -> tp.Optional[int]:
        return getattr(cls, f"_{cls.__name__.lstrip('_')}__abstract_value", None)

    @classmethod
    def get_version(cls) -> tp.Optional[int]:
        return getattr(cls, f"_{cls.__name__.lstrip('_')}__version", None)

    @classmethod
    def get_templates(cls) -> list[TemplateType | TemplateValue]:
        return getattr(cls, f"_{cls.__name__.lstrip('_')}__templates", [])

    @classmethod
    def get_interfaces(cls) -> list[Interface]:
        return getattr(cls, f"_{cls.__name__.lstrip('_')}__interfaces", [])

    @classmethod
    def get_member(cls, member_name: str) -> Member:
        for member in cls.members:
            if member.name == member_name:
                return member
        raise KeyError(f"No member named '{member_name}' in class `{cls.__name__}`.")

    def get_tree_string(self, indent=0, instances_shown: list = None, max_primitive_sequence_size=-1) -> str:
        """Recursively build indented string of this instance and everything within its members."""
        if instances_shown is None:
            instances_shown = []
        lines = [f"{self.__class__.__name__}("]
        for member in self.members:
            member_value = getattr(self, member.name)
            if member_value is None or isinstance(member_value, (bool, int, float, str)):
                lines.append(f"    {member.name} = {repr(member_value)},")
            elif isinstance(member_value, hk):
                if member_value in instances_shown:
                    lines.append(
                        f"    {member.name} = {member_value.__class__.__name__},"
                        f"  # <{instances_shown.index(member_value)}>")
                else:
                    lines.append(
                        f"    {member.name} = "
                        f"{member_value.get_tree_string(indent + 4, instances_shown, max_primitive_sequence_size)},"
                        f"  # <{len(instances_shown)}>"
                    )
                    instances_shown.append(member_value)
            elif isinstance(member_value, list):
                if not member_value:
                    lines.append(f"    {member.name} = [],")
                elif isinstance(member_value[0], hk):
                    lines.append(f"    {member.name} = [")
                    for element in member_value:
                        if element in instances_shown:
                            lines.append(f"        {element.__class__.__name__},  # <{instances_shown.index(element)}>")
                        else:
                            element_string = element.get_tree_string(
                                indent + 8, instances_shown, max_primitive_sequence_size
                            )
                            lines.append(
                                f"        {element_string},  # <{len(instances_shown)}>"
                            )
                            instances_shown.append(element)
                    lines.append(f"    ],")
                elif isinstance(member_value[0], (list, tuple)):
                    if 0 < max_primitive_sequence_size < len(member_value):
                        lines.append(
                            f"    {member.name} = [<{len(member_value)} tuples>],"
                        )
                    else:
                        lines.append(f"    {member.name} = [")
                        for element in member_value:
                            lines.append(f"        {repr(element)},")
                        lines.append(f"    ],")
                else:
                    # Primitive list.
                    if 0 < max_primitive_sequence_size < len(member_value):
                        lines.append(
                            f"    {member.name} = [<{len(member_value)} {type(member_value[0]).__name__}>],"
                        )
                    else:
                        lines.append(f"    {member.name} = {repr(member_value)},")
            elif isinstance(member_value, tuple):
                if not member_value:
                    lines.append(f"    {member.name} = (),")
                elif isinstance(member_value[0], hk):
                    lines.append(f"    {member.name} = (")
                    for element in member_value:
                        if element in instances_shown:
                            lines.append(f"        {element.__class__.__name__},  # <{instances_shown.index(element)}>")
                        else:
                            lines.append(
                                f"        "
                                f"{element.get_tree_string(indent + 8, instances_shown, max_primitive_sequence_size)},"
                                f"  # <{len(instances_shown)}>"
                            )
                            instances_shown.append(element)
                    lines.append(f"    ),")
                elif isinstance(member_value[0], (list, tuple)):
                    lines.append(f"    {member.name} = (")
                    for element in member_value:
                        lines.append(f"        {repr(element)},")
                    lines.append(f"    ),")
                else:
                    lines.append(f"    {member.name} = {repr(member_value)},")
            else:
                raise TypeError(f"Cannot parse value of member '{member.name}' for tree string: {type(member_value)}")
        lines.append(")")
        return f"\n{' ' * indent}".join(lines)

    def __repr__(self):
        return f"{type(self).__name__}()"


class hkBasePointer(hk):
    """Intermediate base type shared by types with a `_data_type` attribute and `get_data_type()` method."""
    _data_type = None  # type: tp.Type[hk] | DefType

    @classmethod
    def get_data_type(cls):
        if isinstance(cls._data_type, DefType):
            cls._data_type = cls._data_type.action()
            return cls._data_type
        return cls._data_type

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        """Default implementation for pointer classes."""
        type_info = super().get_type_info()
        type_info.pointer_type_py_name = cls.get_data_type().__name__
        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-3])  # exclude this, `hk`, and `object`


class TypeInfoGenerator:
    """Builds ordered types by searching each `TagFileItem`, in order."""

    _DEBUG_PRINT = False

    def __init__(self, items: list[TagFileItem | PackFileItemEntry], hk_types_module):
        self._checked_hk = set()
        self.type_infos = {}  # type: dict[str, TypeInfo]
        self._module = hk_types_module
        self._scanned_type_names = set()

        for item in items:
            if isinstance(item.value, hk):
                item_type = type(item.value)  # may be a subclass of `item.hk_type`
            else:
                item_type = item.hk_type
            if self._DEBUG_PRINT:
                print(f"{Fore.BLUE}Scanning item: {item_type.__name__}{Fore.RESET}")
            self._scan_hk_type_queue(deque([item_type]), indent=0)
            if item_type.__name__ == "hkRootLevelContainer":
                self._add_type(getattr(self._module, "_char"))

    def _add_type(self, hk_type: tp.Type[hk], indent=0):
        if hk_type.__name__ in self.type_infos:
            raise KeyError(f"Type named '{hk_type.__name__}' was collected more than once.")
        type_info_index = len(self.type_infos) + 1
        self.type_infos[hk_type.__name__] = hk_type.get_type_info()
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}  {Fore.GREEN}Created TypeInfo {type_info_index}: {hk_type.__name__}{Fore.RESET}")

    def _scan_hk_type_queue(self, hk_type_queue: deque[tp.Type[hk]], indent=0):
        hk_type_subqueue = deque()  # type: deque[tp.Type[hk]]

        while hk_type_queue:
            hk_type = hk_type_queue.popleft()
            self._scan_hk_type(hk_type, hk_type_subqueue, indent + 4)

        if hk_type_subqueue:
            self._scan_hk_type_queue(hk_type_subqueue, indent + 4)

    def _scan_hk_type(self, hk_type: tp.Type[hk], hk_type_queue: deque[tp.Type[hk]], indent=0):
        if hk_type.__name__ in self._scanned_type_names:
            return
        if self._DEBUG_PRINT:
            print(f"{' ' * indent}{Fore.YELLOW}Scanning type: {hk_type.__name__}{Fore.RESET}")
        self._scanned_type_names.add(hk_type.__name__)

        if hk_type.__name__ not in self.type_infos:
            self._add_type(hk_type, indent)

        if issubclass(hk_type, hkEnum_):
            if hk_type.storage_type.__name__ not in self.type_infos:
                self._add_type(hk_type.storage_type, indent)
                hk_type_queue.append(hk_type.storage_type)
            if hk_type.enum_type.__name__ not in self.type_infos:
                self._add_type(hk_type.enum_type, indent)
                hk_type_queue.append(hk_type.enum_type)

        # We don't add the entire hierarchy here. When each parent type is reached, its parents in turn will be reached.
        parent_hk_type = hk_type.get_immediate_parent()
        if parent_hk_type and parent_hk_type.__name__ not in self.type_infos:
            self._add_type(parent_hk_type, indent)
            hk_type_queue.append(parent_hk_type)

        for template_info in hk_type.get_templates():
            if isinstance(template_info, TemplateType):
                if issubclass(template_info.type, hk) and template_info.type.__name__ not in self.type_infos:
                    self._add_type(template_info.type, indent)
                    hk_type_queue.append(template_info.type)

        if issubclass(hk_type, hkBasePointer):
            data_type = hk_type.get_data_type()  # type: tp.Type[hk]

            if issubclass(data_type, hk) and data_type.__name__ not in self.type_infos:
                self._add_type(data_type, indent)
                hk_type_queue.append(data_type)

            if issubclass(hk_type, hkArray_):
                if "hkContainerHeapAllocator" not in self.type_infos:
                    self._add_type(getattr(self._module, "hkContainerHeapAllocator"), indent)
                    # Does not need to be queued.
                if f"Ptr[{data_type.__name__}]" not in self.type_infos:
                    self._add_type(Ptr(data_type), indent)
                    # Does not need to be queued.
                if "_int" not in self.type_infos:
                    self._add_type(getattr(self._module, "_int"), indent)
                    # Does not need to be queued.

            if issubclass(hk_type, (hkRefPtr_, hkRefVariant_)):
                if f"Ptr[{data_type.__name__}]" not in self.type_infos:
                    self._add_type(Ptr(data_type), indent)
                    # Does not need to be queued.

        # if not issubclass(hk_type, hkStruct_):  # struct member types are covered by pointer data type above
        for member in hk_type.local_members:
            if issubclass(member.type, hk) and member.type.__name__ not in self.type_infos:
                self._add_type(member.type, indent)
                hk_type_queue.append(member.type)

        for interface in hk_type.get_interfaces():
            if issubclass(interface.type, hk) and interface.type not in self.type_infos:
                self._add_type(interface.type, indent)
                hk_type_queue.append(interface.type)


# --- GENERIC CLASS BASES & GENERATORS --- #


class hkContainerHeapAllocator(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 16
    local_members = ()


class hkArray_(hkBasePointer):
    """Array base class, which is used to generate subclasses dynamically for different data types.

    The array template 'tT' is always a T* pointer to type `data_type`, and member `m_data` is a pointer to that pointer
    type (the first item in the array). These details aren't needed for actually unpacking and repacking data, though.

    Other hkArray properties, like `tAllocator` and `m_size`, are constant and can be automatically generated.
    """
    alignment = 8  # actually aligned to 16 in tag file data
    byte_size = 16
    tag_type_flags = 8

    __tag_format_flags = 43

    _data_type: tp.Type[hk] | hkRefPtr | hkViewPtr | DefType

    @classmethod
    def unpack(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> list:
        reader.seek(offset)
        _debug_print_unpack(f"Unpacking `{cls.__name__}`...")
        _increment_debug_indent()
        value = unpack_array(cls.get_data_type(), reader, items)
        _decrement_debug_indent()
        _debug_print_unpack(f"-> {repr(value)}")
        if _REQUIRE_INPUT:
            input("Continue?")
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItemEntry, offset: int = None, pointer_size=8):
        offset = entry.reader.seek(offset) if offset is not None else entry.reader.position
        _debug_print_unpack(f"Unpacking `{cls.__name__}`... <{hex(offset)}>")
        _increment_debug_indent()
        value = unpack_array_packfile(cls.get_data_type(), entry, pointer_size=pointer_size)
        _decrement_debug_indent()
        _debug_print_unpack(f"-> {repr(value)}")
        if _REQUIRE_INPUT:
            input("Continue?")
        entry.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack(
        cls,
        item: TagFileItem,
        value: list[hk] | list[int] | list[float] | list[str] | list[bool],
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        """Remember that array length can be variable, unlike `hkStruct`."""
        _debug_print_pack(f"Packing `{cls.__name__}`... (length = {len(value)})")
        pack_array(cls, item, value, items, existing_items, item_creation_queue)
        if _REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItemEntry,
        value: list[hk] | list[int] | list[float] | list[str] | list[bool],
        existing_items: dict[hk, PackFileItemEntry],
        data_pack_queue: dict[str, deque[tp.Callable]],
        pointer_size: int,
    ):
        """Remember that array length can be variable, unlike `hkStruct`."""
        _debug_print_pack(f"Packing `{cls.__name__}`... (length = {len(value)})")
        pack_array_packfile(cls, item, value, existing_items, data_pack_queue, pointer_size)
        if _REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        data_type_py_name = cls.get_data_type().__name__
        type_info = TypeInfo("hkArray")
        type_info.py_class = cls

        type_info.templates = [
            TemplateInfo("tT", type_py_name=data_type_py_name),
            TemplateInfo("tAllocator", type_py_name="hkContainerHeapAllocator"),
        ]
        type_info.tag_format_flags = 43
        type_info.tag_type_flags = 8
        type_info.byte_size = 16
        type_info.alignment = 8
        if (hsh := cls.__dict__.get("__hsh")) is not None:
            type_info.hsh = hsh
        type_info.pointer_type_py_name = data_type_py_name
        type_info.members = [
            # `m_data` generic T* pointer type will be created by caller if missing
            MemberInfo("m_data", flags=34, offset=0, type_py_name=f"Ptr[{data_type_py_name}]"),
            MemberInfo("m_size", flags=34, offset=8, type_py_name="_int"),
            MemberInfo("m_capacityAndFlags", flags=34, offset=12, type_py_name="_int"),
        ]

        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-4])  # exclude this, `hkBasePointer`, `hk`, and `object`


def hkArray(data_type: tp.Type[hk] | hkRefPtr | hkViewPtr, hsh: int = None) -> tp.Type[hkArray_]:
    """Generates an array class with given `data_type` and (optionally) hash."""
    # noinspection PyTypeChecker
    array_type = type(f"hkArray[{data_type.__name__}]", (hkArray_,), {})  # type: tp.Type[hkArray_]
    array_type._data_type = data_type
    array_type.__hsh = hsh
    return array_type


class hkEnum_(hk):
    """Base for simple wrapper types (generated with `hkEnum` function below) that combines a storage type with a
    data type (whose sizes may not match). The name of the enum class is given by the data type. The storage type is
    usually `hkUint8`.

    Note that it is actually possible to extract enum value names from packfiles.
    """
    enum_type = None  # type: tp.Type[hk]
    storage_type = None  # type: tp.Type[hk]

    @classmethod
    def unpack(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = ()):
        # TODO: Parse using storage type or data type? Storage, I think...
        return cls.storage_type.unpack(reader, offset, items)

    @classmethod
    def unpack_packfile(cls, entry: PackFileItemEntry, offset: int = None, pointer_size=8):
        # TODO: Parse using storage type or data type? Storage, I think...
        return cls.storage_type.unpack_packfile(entry, offset, pointer_size=pointer_size)

    @classmethod
    def pack(
        cls,
        item: TagFileItem,
        value: tp.Any,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        return cls.storage_type.pack(item, value, items, existing_items, item_creation_queue)

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItemEntry,
        value: tp.Any,
        existing_items: dict[hk, PackFileItemEntry],
        data_pack_queue: dict[str, deque[tp.Callable]],
        pointer_size: int,
    ):
        return cls.storage_type.pack_packfile(item, value, existing_items, data_pack_queue, pointer_size)

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        type_info = TypeInfo("hkEnum")
        type_info.py_class = cls

        type_info.templates = [
            TemplateInfo("tENUM", type_py_name=cls.enum_type.__name__),
            TemplateInfo("tSTORAGE", type_py_name=cls.storage_type.__name__),
        ]
        type_info.parent_type_py_name = cls.storage_type.__name__
        type_info.tag_format_flags = 0
        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-3])  # exclude this, `hk`, and `object`


def hkEnum(enum_type: tp.Type[hk], storage_type: tp.Type[hk]) -> tp.Type[hkEnum_]:
    """Generates a `_hkEnum` subclass dynamically."""
    # noinspection PyTypeChecker
    wrapper_type = type(f"hkEnum[{enum_type.__name__}]", (hkEnum_,), {})  # type: tp.Type[hkEnum_]
    wrapper_type.enum_type = enum_type
    wrapper_type.storage_type = storage_type
    return wrapper_type


class hkStruct_(hkBasePointer):
    """Simple wrapper type for both 'T[N]' types and built-in tuple types like `hkVector4f`.

    These types store a fixed amount of data locally (e.g., within the same item) rather than separately, like arrays.

    NOTE: For generic 'T[N]' tuples, length is actually stored twice: in the 'vN' template, and in the second most
    significant byte of `tag_type_flags`. (In non-generic tuples, there is no 'vN' template, just the `tag_type_flags`.)
    """
    length = 0
    is_generic = False

    @classmethod
    def unpack(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> tuple:
        reader.seek(offset)
        _debug_print_unpack(f"Unpacking `{cls.__name__}`... (Struct) <{hex(offset)}>")
        _increment_debug_indent()
        value = unpack_struct(cls.get_data_type(), reader, items, cls.length)
        _decrement_debug_indent()
        _debug_print_unpack(f"-> {repr(value)}")
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItemEntry, offset: int = None, pointer_size=8) -> tuple:
        offset = entry.reader.seek(offset) if offset is not None else entry.reader.position
        _debug_print_unpack(f"Unpacking `{cls.__name__}`... (Struct) <{hex(offset)}>")
        _increment_debug_indent()
        value = unpack_struct_packfile(cls.get_data_type(), entry, pointer_size=pointer_size, length=cls.length)
        _decrement_debug_indent()
        _debug_print_unpack(f"-> {repr(value)}")
        entry.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack(
        cls,
        item: TagFileItem,
        value: tp.Any,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        pack_struct(cls.get_data_type(), item, value, items, existing_items, item_creation_queue, cls.length)

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItemEntry,
        value: tp.Any,
        existing_items: dict[hk, PackFileItemEntry],
        data_pack_queue: dict[str, deque[tp.Callable]],
        pointer_size: int,
    ):
        pack_struct_packfile(
            cls.get_data_type(), item, value, existing_items, data_pack_queue, pointer_size, cls.length
        )

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        if cls.is_generic:
            data_type_py_name = cls.get_data_type().__name__
            type_info = TypeInfo("T[N]")
            type_info.py_class = cls
            type_info.pointer_type_py_name = data_type_py_name

            type_info.templates = [
                TemplateInfo("tT", type_py_name=data_type_py_name),
                TemplateInfo("vN", value=cls.length),
            ]
            type_info.tag_format_flags = 11
            type_info.tag_type_flags = cls.tag_type_flags  # already set to correct subtype (including length)
            type_info.byte_size = cls.get_data_type().byte_size * cls.length
            type_info.alignment = cls.get_data_type().alignment
            # TODO: Some generic T[N] types have hashes. Could find it here from XML...
        else:
            # Default method is fine, but we may remove the parent class and add a `data_type` pointer.
            type_info = super().get_type_info()
            type_info.py_class = cls
            type_info.pointer_type_py_name = cls.get_data_type().__name__
            # Immediate children of `hkStruct_` have no parent.
            parent_type = cls.__base__
            if parent_type.__base__ == hkStruct_:
                type_info.parent_type_py_name = None
            # Tag type flags already set.

        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        if cls.is_generic:
            # noinspection PyTypeChecker
            return list(cls.__mro__[:-4])  # exclude this, `hkBasePointer`, `hk`, and `object`
        else:
            # exclude `_hkStruct[type, length]` subclass, this, `hkBasePointer`, `hk`, and `object`
            # noinspection PyTypeChecker
            return list(cls.__mro__[:-5])


def hkStruct(data_type: tp.Type[hk], length: int) -> tp.Type[hkStruct_]:
    """Generates a `_hkStruct` subclass dynamically.

    Needs all the basic `hk` information, unfortunately, as it can vary (except `tag_format_flags`, which is always 11).
    """
    # noinspection PyTypeChecker
    struct_type = type(f"hkStruct[{data_type.__name__}, {length}]", (hkStruct_,), {})  # type: tp.Type[hkStruct_]
    struct_type.is_generic = False
    struct_type._data_type = data_type
    if length > 255:
        raise ValueError(f"Maximum `hkStruct` (`T[N]`) length is 255. Invalid: {length}")
    struct_type.length = length
    struct_type.tag_type_flags = TagDataType.Struct | length << 8
    return struct_type


def hkGenericStruct(data_type: tp.Type[hk], length: int) -> tp.Type[hkStruct_]:
    """Generates a `_hkStruct` subclass dynamically.

    Needs all the basic `hk` information, unfortunately, as it can vary (except `tag_format_flags`, which is always 11).
    """
    # noinspection PyTypeChecker
    struct_type = type(f"hkStruct[{data_type.__name__}, {length}]", (hkStruct_,), {})  # type: tp.Type[hkStruct_]
    struct_type.is_generic = True
    struct_type._data_type = data_type
    if length > 255:
        raise ValueError(f"Maximum `hkStruct` (`T[N]`) length is 255. Invalid: {length}")
    struct_type.length = length
    struct_type.tag_type_flags = TagDataType.Struct | length << 8
    return struct_type


class Ptr_(hkBasePointer):
    """Wrapper for a 'T*' generic pointer, which always points to a fixed type.

    This is necessary because some members, of 'Class' type, use data that is locally stored inside the same item,
    whereas others use these pointers and store their data in different items.

    Differs from `hkRefPtr` below, which has a 'ptr' member of this type and a `tTYPE` template of the pointer's data
    type.
    """
    alignment = 8
    byte_size = 8
    tag_type_flags = 6

    __tag_format_flags = 11

    @classmethod
    def set_data_type(cls, data_type: tp.Type[hk]):
        cls._data_type = data_type

    @classmethod
    def unpack(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> hk:
        """Just a pointer."""
        reader.seek(offset)
        _debug_print_unpack(f"Unpacking `{cls.__name__}`... ({cls.get_tag_data_type().name})")
        value = unpack_pointer(cls.get_data_type(), reader, items)
        _debug_print_unpack(f"-> {value}")
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItemEntry, offset: int = None, pointer_size=8):
        offset = entry.reader.seek(offset) if offset is not None else entry.reader.position
        _debug_print_unpack(f"Unpacking `{cls.__name__}`... (-> {cls.get_tag_data_type().name}) <{hex(offset)}>")
        value = unpack_pointer_packfile(cls.get_data_type(), entry, pointer_size=pointer_size)
        _debug_print_unpack(f"-> {value}")
        entry.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack(
        cls,
        item: TagFileItem,
        value: hk,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        _debug_print_pack(f"Packing `{cls.__name__}`...")
        pack_pointer(cls, item, value, items, existing_items, item_creation_queue)
        if _REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItemEntry,
        value: hk,
        existing_items: dict[hk, PackFileItemEntry],
        data_pack_queue: dict[str, deque[tp.Callable]],
        pointer_size: int,
    ):
        _debug_print_pack(f"Packing `{cls.__name__}`...")
        pack_pointer_packfile(cls, item, value, existing_items, data_pack_queue, pointer_size)
        if _REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        pointer_type_py_name = cls.get_data_type().__name__
        type_info = TypeInfo("T*")

        type_info.templates = [TemplateInfo("tT", type_py_name=pointer_type_py_name)]
        type_info.pointer_type_py_name = pointer_type_py_name
        type_info.tag_format_flags = 11
        type_info.tag_type_flags = 6
        type_info.byte_size = 8
        type_info.alignment = 8
        if (hsh := cls.__dict__.get("__hsh")) is not None:
            type_info.hsh = hsh
        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-4])  # exclude this, `hkBasePointer`, `hk`, and `object`


def Ptr(data_type: tp.Type[hk] | DefType, hsh: int = None) -> tp.Type[Ptr_]:
    """Create a `_Ptr` subclass dynamically, pointing to a particular type."""
    data_type_name = data_type.type_name if isinstance(data_type, DefType) else data_type.__name__
    # noinspection PyTypeChecker
    ptr_type = type(f"Ptr[{data_type_name}]", (Ptr_,), {})  # type: tp.Type[Ptr_]
    ptr_type._data_type = data_type
    ptr_type.__hsh = hsh
    return ptr_type


class hkReflectQualifiedType_(Ptr_):
    """Simple wrapper for a special pointer type that has a `tTYPE` template with type `hkReflectType` and a `type`
    member that always points to `hkReflectType`.
    
    This pointer never actually varies, and presumably just indicates some reflective member that doesn't matter for
    our purposes here.
    """
    alignment = 8
    byte_size = 8
    tag_type_flags = 6

    __tag_format_flags = 43

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-5])  # exclude this, `_Ptr`, `hkBasePointer`, `hk`, and `object`

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        type_info = TypeInfo("hkReflect::QualifiedType")
        type_info.py_class = cls

        type_info.templates = [
            TemplateInfo("tTYPE", type_py_name="hkReflectType"),
        ]
        type_info.tag_format_flags = 43
        type_info.tag_type_flags = 6
        type_info.byte_size = 8
        type_info.alignment = 8
        if (hsh := cls.__dict__.get("__hsh")) is not None:
            type_info.hsh = hsh
        type_info.pointer_type_py_name = "hkReflectType"
        type_info.members = [
            MemberInfo("type", flags=36, offset=0, type_py_name=f"Ptr[hkReflectType]"),
        ]

        return type_info


class hkRefPtr_(Ptr_):
    """Simple wrapper for a special pointer type that has a `tTYPE` template and a `ptr` member that always points to
    some instance of the `tTYPE`.

    For example, the 'skeletons' member of `hkaAnimationContainer` is an array of `hkRefPtr`s. The array itself uses
    one T* pointer for its `m_data` attribute, and each `hkRefPtr` in the array has its own T* pointer as its `ptr`
    member, whose data type is always the same as the `tTYPE` template of the `hkRefPtr`.

    Not sure exactly why this is used instead of a generic 'T*' `Ptr` in some cases.

    TODO: Some `hkRefPtr` classes have hashes in XML. In fact, I think some T* generic pointers do too...
    """
    alignment = 8
    byte_size = 8
    tag_type_flags = 6

    __tag_format_flags = 43

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-5])  # exclude this, `_Ptr`, `hkBasePointer`, `hk`, and `object`

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        type_info = TypeInfo("hkRefPtr")
        type_info.py_class = cls

        type_info.templates = [
            TemplateInfo("tTYPE", type_py_name=cls.get_data_type().__name__),
        ]
        type_info.tag_format_flags = 43
        type_info.tag_type_flags = 6
        type_info.byte_size = 8
        type_info.alignment = 8
        if (hsh := cls.__dict__.get("__hsh")) is not None:
            type_info.hsh = hsh
        type_info.pointer_type_py_name = cls.get_data_type().__name__
        type_info.members = [
            MemberInfo("ptr", flags=36, offset=0, type_py_name=f"Ptr[{cls.get_data_type().__name__}]"),
        ]

        return type_info


def hkRefPtr(data_type: tp.Type[hk] | DefType, hsh: int = None) -> tp.Type[hkRefPtr_]:
    """Create a `_hkRefPtr` subclass dynamically, pointing to a particular type."""
    data_type_name = data_type.type_name if isinstance(data_type, DefType) else data_type.__name__
    # noinspection PyTypeChecker
    ptr_type = type(f"hkRefPtr[{data_type_name}]", (hkRefPtr_,), {})  # type: tp.Type[hkRefPtr_]
    ptr_type._data_type = data_type
    ptr_type.__hsh = hsh
    return ptr_type


class hkRefVariant_(Ptr_):
    """Points to some `hkReferencedObject` subclass, and has no template."""
    __tag_format_flags = 43

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-5])  # exclude this, `Ptr_`, `hkBasePointer`, `hk`, and `object`

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        type_info = TypeInfo("hkRefVariant")
        type_info.py_class = cls

        type_info.tag_format_flags = 43
        type_info.tag_type_flags = 6
        type_info.byte_size = 8
        type_info.alignment = 8
        if (hsh := cls.__dict__.get("__hsh")) is not None:
            type_info.hsh = hsh
        type_info.pointer_type_py_name = cls.get_data_type().__name__
        type_info.members = [
            MemberInfo("ptr", flags=36, offset=0, type_py_name=f"Ptr[{cls.get_data_type().__name__}]"),
        ]

        return type_info


def hkRefVariant(data_type: tp.Type[hk] | DefType, hsh: int = None) -> tp.Type[hkRefVariant_]:
    """Create a `hkRefVariant_` subclass dynamically, pointing to a particular type.

    Note that the pointed type must always be "hkReferencedObject".
    """
    data_type_name = data_type.__name__
    if data_type_name != "hkReferencedObject":
        raise ValueError(
            f"`hkRefVariant` was defined with a data type other than `hkReferencedObject`: {data_type_name}"
        )
    # noinspection PyTypeChecker
    ptr_type = type(f"hkRefVariant[{data_type_name}]", (hkRefVariant_,), {})  # type: tp.Type[hkRefVariant_]
    ptr_type._data_type = data_type
    ptr_type.__hsh = hsh
    return ptr_type


class hkViewPtr_(hk):
    """Pointer that is used at least once (by `hkpEntity`) for a recursive look at an owner class
    (`hkpConstraintInstance`).

    This is the only time this circularity appears in the 2015 types, so I don't think it's a coincidence that this
    special pointer is used. Here, it just holds a string name of the reference class, so definition can continue. The
    class can be retrieved by name when needed.
    """
    alignment = 8
    byte_size = 8
    tag_type_flags = 6

    __tag_format_flags = 59
    __abstract_value = 64

    data_type_name = ""

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-3])  # exclude this, `hk`, and `object`

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        type_info = TypeInfo("hkViewPtr")
        type_info.py_class = cls

        type_info.templates = [
            TemplateInfo("tTYPE", type_py_name=cls.data_type_name),
        ]
        type_info.tag_format_flags = 59
        type_info.tag_type_flags = 6
        type_info.byte_size = 8
        type_info.alignment = 8
        type_info.abstract_value = 64
        type_info.pointer_type_py_name = cls.data_type_name
        # `hkViewPtr` hash is actually its pointer's hash; `hkViewPtr` has no hash.
        type_info.members = [
            MemberInfo("ptr", flags=36, offset=0, type_py_name=f"Ptr[{cls.data_type_name}]"),
        ]

        return type_info


def hkViewPtr(data_type_name: str, hsh: int = None):
    """Create a `_hkViewPtr` subclass dynamically, pointing to a particular type name."""
    # noinspection PyTypeChecker
    ptr_type = type(f"hkViewPtr[{data_type_name}]", (hkViewPtr_,), {})  # type: tp.Type[hkViewPtr_]
    ptr_type.data_type_name = data_type_name
    ptr_type.__hsh = hsh
    return ptr_type


class NewStruct_(hkBasePointer):
    """Wrapper for a new type of pointer that only appears in `hknp` classes. (Name chosen by me.)

    It reads `length` and `jump` shorts, and uses that offset to make a jump ahead (from just before `length`) to
    tightly packed struct value of some data type, which is unpacked into a tuple like regular `hkStruct` (`T[N`)
    structs.
    """
    # TODO: No idea what these values should be (except `byte_size = 4`).
    alignment = 4
    byte_size = 4
    tag_type_flags = 6

    __tag_format_flags = 11

    @classmethod
    def set_data_type(cls, data_type: tp.Type[hk]):
        cls._data_type = data_type

    @classmethod
    def unpack(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> hk:
        raise TypeError("Have not encountered `NewStruct` types in tagfiles before. Cannot unpack them.")

    @classmethod
    def unpack_packfile(cls, entry: PackFileItemEntry, offset: int = None, pointer_size=8) -> tuple:
        offset = entry.reader.seek(offset) if offset is not None else entry.reader.position
        _debug_print_unpack(f"Unpacking `{cls.__name__}`... ({cls.get_data_type().__name__}) <{hex(offset)}>")

        source_offset = entry.reader.position
        length, jump = entry.reader.unpack("<HH")
        with entry.reader.temp_offset(source_offset + jump):
            value = unpack_struct_packfile(cls.get_data_type(), entry, pointer_size=pointer_size, length=length)
        _debug_print_unpack(f"-> {value}")
        entry.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack(
        cls,
        item: TagFileItem,
        value: hk,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        raise TypeError("Have not encountered `NewStruct` types in tagfiles before. Cannot pack them.")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItemEntry,
        value: tuple,
        existing_items: dict[hk, PackFileItemEntry],
        data_pack_queue: dict[str, deque[tp.Callable]],
        pointer_size: int,
    ):
        """TODO: Just using a `jump` of 4 for now (skipping `length` and `jump` shorts)."""
        _debug_print_pack(f"Packing `{cls.__name__}`...")
        item.writer.pack("<HH", len(value), 4)
        pack_struct_packfile(cls, item, value, existing_items, data_pack_queue, pointer_size, length=len(value))
        if _REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        raise TypeError("Cannot convert `_NewStruct` to `TypeInfo` yet for packing packfiles.")

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-4])  # exclude this, `hk`, `hkBasePointer`, and `object`


def NewStruct(data_type: tp.Type[hk]):
    """Create a `_NewStruct` subclass dynamically."""
    data_type_name = data_type.type_name if isinstance(data_type, DefType) else data_type.__name__
    # noinspection PyTypeChecker
    struct_type = type(f"NewStruct[{data_type_name}]", (NewStruct_,), {})  # type: tp.Type[NewStruct_]
    struct_type._data_type = data_type
    return struct_type


# --- UNPACKING/PACKING FUNCTIONS --- #


def unpack_bool(hk_type: tp.Type[hk], reader: BinaryReader) -> bool:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt) > 0


def pack_bool(hk_type: tp.Type[hk], item: TagFileItem | PackFileItemEntry, value: bool):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    item.writer.pack(fmt, int(value))


def unpack_int(hk_type: tp.Type[hk], reader: BinaryReader) -> int:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt)


def pack_int(hk_type: tp.Type[hk], item: TagFileItem | PackFileItemEntry, value: int):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags, signed=value < 0)
    item.writer.pack(fmt, value)


def unpack_float32(reader: BinaryReader) -> float | hk:
    """32-bit floats are unpacked directly; others (like half floats) are unpacked as classes (Havok's setup)."""
    return reader.unpack_value("<f")


def pack_float(hk_type: tp.Type[hk], item: TagFileItem, value: float | hk):
    if hk_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
        item.writer.pack("<f", value)
    else:
        # Will definitely not use or create items.
        pack_class(hk_type, item, value, items=[], existing_items={}, item_creation_queue={})


def pack_float_packfile(hk_type: tp.Type[hk], item: PackFileItemEntry, value: float | hk, pointer_size: int):
    if hk_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
        item.writer.pack("<f", value)
    else:
        # Will definitely not use or create items.
        pack_class_packfile(hk_type, item, value, existing_items={}, data_pack_queue={}, pointer_size=pointer_size)


def unpack_class(hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem], instance=None) -> hk:
    """Existing `instance` created by caller can be passed, which is useful for managing recursion.

    NOTE: This is not used for `hkRootLevelContainerNamedVariant`, which uses a special dynamic unpacker to detect the
    appropriate `hkReferencedObject` subclass it points to with its `hkRefVariant` pointer.
    """
    if instance is None:
        instance = hk_type()
    member_start_offset = reader.position

    _increment_debug_indent()
    for member in hk_type.members:
        _debug_print_unpack(f"Member '{member.name}' (type `{member.type.__name__}`):")
        member_value = member.type.unpack(reader, member_start_offset + member.offset, items)
        _debug_print_unpack(f"    -> Real type: {type(member_value).__name__}")
        # TODO: For finding the floor material hex offset in map collisions.
        # if hk_type.__name__ == "_CustomMeshParameter":
        #     print(
        #         f"Custom mesh parameter member {member.name} offset: "
        #         f"{hex(member_start_offset + member.offset)} ({member_value})"
        #     )
        setattr(instance, member.name, member_value)  # type hint will be given in class definition
    _decrement_debug_indent()
    return instance


def unpack_class_packfile(hk_type: tp.Type[hk], entry: PackFileItemEntry, pointer_size: int, instance=None) -> hk:
    """Existing `instance` created by caller can be passed, which is useful for managing recursion.

    NOTE: This is not used for `hkRootLevelContainerNamedVariant`, which uses a special dynamic unpacker to detect the
    appropriate `hkReferencedObject` subclass it points to with its `hkRefVariant` pointer.
    """
    if instance is None:
        instance = hk_type()
    member_start_offset = entry.reader.position

    _increment_debug_indent()
    for member in hk_type.members:
        _debug_print_unpack(f"Member '{member.name}' (type `{member.type.__name__}`):")
        member_value = member.type.unpack_packfile(
            entry,
            offset=member_start_offset + member.offset,
            pointer_size=pointer_size,
        )
        setattr(instance, member.name, member_value)  # type hint will be given in class definition
    _decrement_debug_indent()
    return instance


def pack_class(
    hk_type: tp.Type[hk],
    item: TagFileItem,
    value: hk,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queue: dict[str, deque[tp.Callable]],
):
    member_start_offset = item.writer.position

    _increment_debug_indent()
    for member in hk_type.members:
        _debug_print_pack(f"Member '{member.name}' (type `{member.type.__name__}`):")
        # Member offsets may not be perfectly packed together, so we always pad up to the proper offset.
        item.writer.pad_to_offset(member_start_offset + member.offset)
        member.type.pack(item, value[member.name], items, existing_items, item_creation_queue)
    _decrement_debug_indent()

    item.writer.pad_to_offset(member_start_offset + hk_type.byte_size)


def pack_class_packfile(
    hk_type: tp.Type[hk],
    item: PackFileItemEntry,
    value: hk,
    existing_items: dict[hk, PackFileItemEntry],
    data_pack_queue: dict[str, deque[tp.Callable]],
    pointer_size: int,
):
    member_start_offset = item.writer.position

    if "hkBaseObject" in [parent_type.__name__ for parent_type in hk_type.get_type_hierarchy()]:
        # Pointer for the mysterious base object type.
        item.writer.pad(pointer_size)

    _increment_debug_indent()
    for member in hk_type.members:
        _debug_print_pack(
            f"Member '{member.name}' (type `{type(value[member.name]).__name__} : {member.type.__name__}`):"
        )
        # Member offsets may not be perfectly packed together, so we always pad up to the proper offset.
        item.writer.pad_to_offset(member_start_offset + member.offset)
        # TODO: with_flag = member.name != "partitions" ?
        member.type.pack_packfile(item, value[member.name], existing_items, data_pack_queue, pointer_size)
        # TODO: Needed?
        # if member.type.alignment > 0:
        #     item.writer.pad_align(member.type.alignment)
    _decrement_debug_indent()

    item.writer.pad_to_offset(member_start_offset + hk_type.byte_size)


def unpack_pointer(data_hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem]) -> hk | None:
    item_index = reader.unpack_value("<I")
    _debug_print_unpack(f"`{data_hk_type.__name__}` pointer item index: {item_index}")
    if item_index == 0:
        return None
    try:
        item = items[item_index]
    except IndexError:
        raise IndexError(f"Invalid tag file item index: {item_index}")

    # Check item's type is a subclass of expected `data_hk_type`.
    if not issubclass(item.hk_type, data_hk_type):
        raise TypeError(
            f"Pointer type is `{data_hk_type.__name__}`, but this is not a parent class of actual item type "
            f"`{item.hk_type.__name__}`."
        )

    if item.value is None:  # unpack item and assign unpacked value to it on first encounter in traversal
        if item.in_process:
            # This can only happen for `hkViewPtr`, I believe, and it will only reference classes.
            # Item value has been set to an empty dictionary already in this case, so it can be viewed here too.
            if not item.hk_type.get_tag_data_type() == TagDataType.Class:
                raise AssertionError(f"Found item recursion inside non-class `{item.hk_type.__name__}`.")
        item.in_process = True
        is_named_variant = item.hk_type.__name__ == "hkRootLevelContainerNamedVariant"
        if item.hk_type.get_tag_data_type() == TagDataType.Class and not is_named_variant:
            # Create and assign instance to item here, before unpacker unpacks its members, so recursive views to
            # it can be assigned to the right instance (as `item.value` will not be None next time).
            item.value = item.hk_type()
            reader.seek(item.absolute_offset)
            unpack_class(item.hk_type, reader, items, item.value)
        else:
            # No risk of recursion.
            item.value = item.hk_type.unpack(reader, item.absolute_offset, items)
        item.in_process = False
    return item.value


def unpack_pointer_packfile(data_hk_type: tp.Type[hk], item: PackFileItemEntry, pointer_size: int) -> hk | None:
    """`data_hk_type` is used to make sure that the referenced entry's `hk_type` is a subclass of it."""
    source_offset = item.reader.position
    zero = item.reader.unpack_value("<I" if pointer_size == 4 else "<Q")  # "dummy" pointer
    try:
        item, item_data_offset = item.item_pointers[source_offset]
    except KeyError:
        if zero != 0:
            print(item.item_pointers)
            raise ValueError(
                f"Could not find entry pointer: type {item.hk_type.__name__}, buffer at {hex(source_offset)}."
            )
        else:
            return None
    if zero != 0:
        raise AssertionError(f"Found non-zero data at entry pointer offset: {zero}.")
    if item_data_offset != 0:
        print(item.item_pointers)
        raise AssertionError(f"Data entry pointer (global ref dest) was not zero: {item_data_offset}.")
    if not issubclass(item.hk_type, data_hk_type):
        raise ValueError(
            f"Pointer-referenced entry type {item.hk_type.__name__} is not a child of expected type "
            f"{data_hk_type.__name__}."
        )
    if item.value is None:
        # Unpack entry (first time).
        item.start_reader()
        _increment_debug_indent()
        # NOTE: `item.hk_type` may be a subclass of `data_hk_type`, so it's important we use it here.
        item.value = item.hk_type.unpack_packfile(item, pointer_size=pointer_size)
        _decrement_debug_indent()
    else:
        _debug_print_unpack(f"Existing item: {type(item.value).__name__}")
    return item.value


def pack_pointer(
    ptr_hk_type: tp.Union[tp.Type[Ptr_], tp.Type[NewStruct_]],
    item: TagFileItem,
    value: hk,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queue: dict[str, deque[tp.Callable]],
):
    if value is None:
        item.writer.pack("<I", 0)
        return

    item.patches.setdefault(ptr_hk_type.__name__, []).append(item.writer.position)

    data_hk_type = ptr_hk_type.get_data_type()

    if not isinstance(value, data_hk_type):
        raise TypeError(
            f"Pointer to `{data_hk_type.__name__}` contained wrong type: `{value.__class__.__name__}`"
        )

    # Queues up a function that will create the item and write its offset to this position.
    # No need to reserve an index in the writer; it will be recorded in the function body.

    item_index_pos = item.writer.position
    item.writer.pack("<I", 0)  # temporary

    # print(f"Appending pointer item pack: {value}")

    def delayed_item_creation(_item_creation_queue) -> tp.Optional[TagFileItem]:
        # Item may have been created since this function was queued.
        if value in existing_items:
            existing_item = existing_items[value]
            item.writer.pack_at(item_index_pos, "<I", items.index(existing_item))
            return None

        # print(f"Packing pointer item index {len(items)}")
        item.writer.pack_at(item_index_pos, "<I", len(items))
        value_data_hk_type = type(value)  # type: tp.Type[hk]  # may be a subclass of `data_hk_type`
        new_item = TagFileItem(ptr_hk_type, is_ptr=value_data_hk_type.get_tag_data_type() == TagDataType.Class)
        new_item.value = value
        existing_items[value] = new_item
        items.append(new_item)
        new_item.writer = BinaryWriter()
        # Item does NOT recur `.pack()` here. It is packed when this item is iterated over.
        return new_item

    item_creation_queue.setdefault("pointer", deque()).append(delayed_item_creation)


def pack_pointer_packfile(
    data_hk_type: tp.Type[hk],
    item: PackFileItemEntry,
    value: hk,
    existing_items: dict[hk, PackFileItemEntry],
    data_pack_queue: dict[str, deque[tp.Callable]],
    pointer_size: int,
):
    if value in existing_items:
        item.item_pointers[item.writer.position] = (existing_items[value], 0)
        item.writer.pad(pointer_size)  # global item fixup
        _debug_print_pack(f"Existing item: {type(existing_items[value]).__name__}")
        return
    else:
        # NOTE: This uses the data type, NOT the `Ptr` type.
        new_item = existing_items[value] = PackFileItemEntry(data_hk_type)
        new_item.value = value
        item.item_pointers[item.writer.position] = (new_item, 0)
        item.writer.pad(pointer_size)  # global item fixup
        _debug_print_pack(f"Creating new item and queuing data pack: {type(new_item.value).__name__}")

    def delayed_data_pack(_data_pack_queue) -> PackFileItemEntry:
        new_item.start_writer()
        value.pack_packfile(new_item, value, existing_items, _data_pack_queue, pointer_size)
        _debug_print_pack(f"Packing data for item: {type(new_item.value).__name__}")
        return new_item

    data_pack_queue.setdefault("pointer", deque()).append(delayed_data_pack)


def unpack_array(data_hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem]) -> list:
    item_index = reader.unpack_value("<I")
    _debug_print_unpack(f"Array item index: {item_index} (type `{data_hk_type.__name__}`)")
    if item_index == 0:
        return []
    item = items[item_index]

    if item.value is None:
        _increment_debug_indent()
        item.value = [
            data_hk_type.unpack(
                reader,
                offset=item.absolute_offset + i * data_hk_type.byte_size,
                items=items,
            ) for i in range(item.length)
        ]
        _decrement_debug_indent()
    return item.value


def unpack_array_packfile(data_hk_type: tp.Type[hk], entry: PackFileItemEntry, pointer_size: int) -> list:
    array_pointer_offset = entry.reader.position
    zero, array_size, array_capacity_and_flags = entry.reader.unpack("<III" if pointer_size == 4 else "<QII")
    _debug_print_unpack(f"Array size and cap/flags: {array_size}, {array_capacity_and_flags}")
    if zero != 0:
        print(f"Zero, array_size, array_caps_flags: {zero, array_size, array_capacity_and_flags}")
        print(f"Entry child pointers: {entry.child_pointers}")
        print(f"Entry entry pointers: {entry.item_pointers}")
        print(f"Entry raw data:\n{get_hex_repr(entry.raw_data)}")
        raise AssertionError(f"Found non-null data at child pointer offset {hex(array_pointer_offset)}: {zero}")

    if array_size == 0:
        return []

    array_data_offset = entry.child_pointers[array_pointer_offset]

    _increment_debug_indent()
    with entry.reader.temp_offset(array_data_offset):
        value = [
            data_hk_type.unpack_packfile(
                entry,
                # no offset needed, as array elements are tightly packed
                pointer_size=pointer_size,
            ) for _ in range(array_size)
        ]
    _decrement_debug_indent()

    return value


def pack_array(
    array_hk_type: tp.Type[hkArray_],
    item: TagFileItem,
    value: list[hk | str | int | float | bool],
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queue: dict[str, deque[tp.Callable]],
):
    """Array items are always created per instance, never re-used. (Not sure if that's correct, but it is here.)"""
    if not value:
        item.writer.pack("<I", 0)
        return

    # Queues up a function that will create the item and write its item index to this position.
    # No need to reserve an index in the writer; it will be recorded in the function body.

    item_index_pos = item.writer.position
    item.writer.pack("<I", 0)  # temporary
    data_hk_type = array_hk_type.get_data_type()

    # print(f"Appending array item pack: {value}")

    def delayed_item_creation(_item_creation_queue) -> TagFileItem:
        # print(f"Packing array item index {len(items)}")
        item.writer.pack_at(item_index_pos, "<I", len(items))
        new_item = TagFileItem(array_hk_type, is_ptr=False, length=len(value))
        item.patches.setdefault(new_item.hk_type.__name__, []).append(item_index_pos)
        new_item.value = value
        items.append(new_item)
        new_item.writer = BinaryWriter()
        for i, element in enumerate(value):
            data_hk_type.pack(new_item, element, items, existing_items, _item_creation_queue)
            new_item.writer.pad_to_offset((i + 1) * data_hk_type.byte_size)
        return new_item

    item_creation_queue.setdefault("array", deque()).append(delayed_item_creation)


def pack_array_packfile(
    array_hk_type: tp.Type[hkArray_],
    item: PackFileItemEntry,
    value: list[hk | str | int | float | bool],
    existing_items: dict[hk, PackFileItemEntry],
    data_pack_queue: dict[str, deque[tp.Callable]],
    pointer_size: int,
    with_flag=True,  # TODO: only found one array that doesn't use the flag (hkaBone["partitions"]).
):
    array_ptr_pos = item.writer.position
    item.writer.pad(pointer_size)  # where the fixup would go, if it was actually resolved
    item.writer.pack("<I", len(value))  # array length
    # Capacity is same as length, and highest bit is enabled (flags "do not free memory", I believe).
    item.writer.pack("<I", len(value) | (1 << 31 if with_flag else 0))  # highest bit on
    data_hk_type = array_hk_type.get_data_type()

    if not value:
        return  # empty

    def delayed_data_write(_data_pack_queue):
        """Delayed writing of array data until later in the same packfile item."""

        _sub_data_pack_queue = {"pointer": deque(), "array_or_string": deque()}
        item.writer.pad_align(16)  # pre-align for array
        item.child_pointers[array_ptr_pos] = item.writer.position  # fixup
        array_start_offset = item.writer.position
        for i, element in enumerate(value):
            data_hk_type.pack_packfile(item, element, existing_items, _sub_data_pack_queue, pointer_size)
            item.writer.pad_to_offset(array_start_offset + (i + 1) * data_hk_type.byte_size)

        # Immediately recur on any new array/string data queued up (i.e., depth-first for packing arrays and strings).
        while _sub_data_pack_queue["array_or_string"]:
            _sub_data_pack_queue["array_or_string"].popleft()(_sub_data_pack_queue)
        # Pass on pointers to higher queue.
        while _sub_data_pack_queue["pointer"]:
            _data_pack_queue.setdefault("pointer", deque()).append(_sub_data_pack_queue["pointer"].popleft())

    data_pack_queue["array_or_string"].append(delayed_data_write)


def unpack_struct(
    data_hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem], length: int
) -> tuple:
    struct_start_offset = reader.position
    return tuple(
        data_hk_type.unpack(
            reader,
            offset=struct_start_offset + i * data_hk_type.byte_size,
            items=items,
        ) for i in range(length)
    )


def unpack_struct_packfile(
    data_hk_type: tp.Type[hk], entry: PackFileItemEntry, pointer_size: int, length: int
) -> tuple:
    """Identical to tagfile (just different recursive method)."""
    struct_start_offset = entry.reader.position
    return tuple(
        data_hk_type.unpack_packfile(
            entry,
            offset=struct_start_offset + i * data_hk_type.byte_size,
            pointer_size=pointer_size,
        ) for i in range(length)
    )


def pack_struct(
    data_hk_type: tp.Type[hk],
    item: TagFileItem,
    value: tuple,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queue: dict[str, deque[tp.Callable]],
    length: int,
):
    """Structs are packed locally in the same item, but can contain pointers themselves."""
    struct_start_offset = item.writer.position
    if len(value) != length:
        raise ValueError(f"Length of `{data_hk_type.__name__}` value is not {length}: {value}")
    for i, element in enumerate(value):
        item.writer.pad_to_offset(struct_start_offset + i * data_hk_type.byte_size)
        data_hk_type.pack(item, element, items, existing_items, item_creation_queue)


def pack_struct_packfile(
    data_hk_type: tp.Type[hk],
    item: PackFileItemEntry,
    value: tuple,
    existing_items: dict[hk, PackFileItemEntry],
    data_pack_queue: dict[str, deque[tp.Callable]],
    pointer_size: int,
    length: int,
):
    """Structs are packed locally in the same item, but can contain pointers themselves."""
    struct_start_offset = item.writer.position
    if len(value) != length:
        raise ValueError(f"Length of `{data_hk_type.__name__}` value is not {length}: {value}")
    for i, element in enumerate(value):
        item.writer.pad_to_offset(struct_start_offset + i * data_hk_type.byte_size)
        data_hk_type.pack_packfile(item, element, existing_items, data_pack_queue, pointer_size)


def unpack_string(reader: BinaryReader, items: list[TagFileItem]) -> str:
    """Nothing more than an array of `char` bytes (standard `const char*`)."""
    item_index = reader.unpack_value("<I")
    _debug_print_unpack(f"String item index: {item_index}")
    if item_index == 0:
        return ""
    item = items[item_index]
    if item.value is None:
        reader.seek(item.absolute_offset)
        encoded = reader.read(item.length)
        item.value = encoded.decode("shift_jis_2004").rstrip("\0")
    return item.value


def unpack_string_packfile(entry: PackFileItemEntry, pointer_size: int) -> str:
    """Read a null-terminated string from entry child pointer."""
    pointer_offset = entry.reader.position
    entry.reader.unpack_value("<I" if pointer_size == 4 else "<Q", asserted=0)
    try:
        string_offset = entry.child_pointers[pointer_offset]
    except KeyError:
        return ""
    return entry.reader.unpack_string(offset=string_offset, encoding="shift_jis_2004")


def pack_string(
    string_hk_type: tp.Type[hk],
    item: TagFileItem,
    value: str,
    items: list[TagFileItem],
    item_creation_queue: dict[str, deque[tp.Callable]],
    is_variant_name=False,
):
    """Like arrays (which they are, essentially), strings are never re-used as items."""
    item.patches.setdefault(string_hk_type.__name__, []).append(item.writer.position)

    if not value:
        item.writer.pack("<I", 0)
        return
    if not isinstance(value, str):
        raise ValueError(f"Cannot pack non-string: {value}")

    item_index_pos = item.writer.position
    item.writer.pack("<I", 0)  # temporary

    def delayed_item_creation(_item_creation_queue) -> TagFileItem:
        # print(f"Packing string item index {len(items)}")
        item.writer.pack_at(item_index_pos, "<I", len(items))
        encoded = value.encode("shift_jis_2004") + b"\0"
        new_item = TagFileItem(string_hk_type, is_ptr=False, length=len(encoded))
        new_item.value = value
        items.append(new_item)
        new_item.writer = BinaryWriter()
        new_item.writer.append(encoded)  # could write `data` immediately but this is more consistent
        return new_item

    if is_variant_name:
        item_creation_queue.setdefault("variant_name_string", deque()).append(delayed_item_creation)
    else:
        item_creation_queue.setdefault("string", deque()).append(delayed_item_creation)


def pack_string_packfile(
    item: PackFileItemEntry,
    value: str,
    data_pack_queue: dict[str, deque[tp.Callable]],
    pointer_size: int,
):
    """Note that string type (like `hkStringPtr`) is never explicitly defined in packfiles, since they do not have
    their own items, unlike in tagfiles."""
    string_ptr_pos = item.writer.position
    item.writer.pad(pointer_size)  # where fixup would be resolved

    if not value:
        return  # empty strings have no fixup

    def delayed_string_write(_item_creation_queue):
        item.child_pointers[string_ptr_pos] = item.writer.position
        item.writer.append(value.encode("shift_jis_2004") + b"\0")
        item.writer.pad_align(16)

    data_pack_queue.setdefault("array_or_string", deque()).append(delayed_string_write)


def unpack_named_variant(
    hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem], types_module: dict
) -> hk:
    """Detects `variant` type dynamically from `className` member."""
    instance = hk_type()
    member_start_offset = reader.position
    # "variant" member type is a subclass of `hkReferencedObject` with name "className".
    name_member, class_name_member, variant_member = hk_type.members[:3]
    name = name_member.type.unpack(
        reader, member_start_offset + name_member.offset, items
    )
    setattr(instance, name_member.name, name)
    variant_type_name = class_name_member.type.unpack(
        reader, member_start_offset + class_name_member.offset, items
    )
    setattr(instance, class_name_member.name, variant_type_name)
    variant_py_name = get_py_name(variant_type_name)
    variant_type = types_module[variant_py_name]
    reader.seek(member_start_offset + variant_member.offset)
    _debug_print_unpack(f"Unpacking named variant: {hk_type.__name__}... <{reader.position_hex}>")
    _increment_debug_indent()
    variant_instance = unpack_pointer(variant_type, reader, items)
    _decrement_debug_indent()
    _debug_print_unpack(f"--> {variant_instance}")
    setattr(instance, variant_member.name, variant_instance)
    return instance


def unpack_named_variant_packfile(
    hk_type: tp.Type[hk], entry: PackFileItemEntry, pointer_size: int, types_module: dict
) -> hk:
    """Detects `variant` type dynamically from `className` member."""
    instance = hk_type()
    member_start_offset = entry.reader.position
    # "variant" member type is a subclass of `hkReferencedObject` with name "className".
    name_member, class_name_member, variant_member = hk_type.members[:3]
    name = name_member.type.unpack_packfile(
        entry, offset=member_start_offset + name_member.offset, pointer_size=pointer_size
    )
    setattr(instance, name_member.name, name)
    variant_type_name = class_name_member.type.unpack_packfile(
        entry, offset=member_start_offset + class_name_member.offset, pointer_size=pointer_size
    )
    setattr(instance, class_name_member.name, variant_type_name)
    variant_py_name = get_py_name(variant_type_name)
    variant_type = types_module[variant_py_name]
    entry.reader.seek(member_start_offset + variant_member.offset)
    _debug_print_unpack(f"Unpacking named variant: {hk_type.__name__}... <{entry.reader.position_hex}>")
    _increment_debug_indent()
    variant_instance = unpack_pointer_packfile(variant_type, entry, pointer_size=pointer_size)
    _decrement_debug_indent()
    _debug_print_unpack(f"--> {variant_instance}")
    setattr(instance, variant_member.name, variant_instance)
    return instance


def pack_named_variant(
    hk_type: tp.Type[hk],
    item: TagFileItem,
    value: hk,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queue: dict[str, deque[tp.Callable]],
):
    """Named variants create items for their 'name' members before their 'className' members."""
    member_start_offset = item.writer.position
    _increment_debug_indent()

    name_member = hk_type.members[0]
    item.writer.pad_to_offset(member_start_offset + name_member.offset)
    _debug_print_pack(f"Member 'name' (type `{name_member.type.__name__}`):")
    # noinspection PyArgumentList
    name_member.type.pack(item, value["name"], items, existing_items, item_creation_queue, is_variant_name=True)

    class_name_member = hk_type.members[1]
    item.writer.pad_to_offset(member_start_offset + class_name_member.offset)
    _debug_print_pack(f"Member 'className' (type `{class_name_member.type.__name__}`):")
    class_name_member.type.pack(item, value["className"], items, existing_items, item_creation_queue)

    variant_member = hk_type.members[2]
    item.writer.pad_to_offset(member_start_offset + variant_member.offset)
    _debug_print_pack(f"Member 'variant' (type `{variant_member.type.__name__}`):")
    variant_member.type.pack(item, value["variant"], items, existing_items, item_creation_queue)

    _decrement_debug_indent()


def pack_named_variant_packfile(
    hk_type: tp.Type[hk],
    item: PackFileItemEntry,
    value: hk,
    existing_items: dict[hk, PackFileItemEntry],
    data_pack_queue: dict[str, deque[tp.Callable]],
    pointer_size: int,
):
    """TODO: Actually no different from `pack_class_packfile()`, because packfiles don't need `className` first."""
    member_start_offset = item.writer.position
    _increment_debug_indent()

    name_member = hk_type.members[0]
    item.writer.pad_to_offset(member_start_offset + name_member.offset)
    _debug_print_pack(f"Member 'name' (type `{name_member.type.__name__}`):")
    # `is_variant_name` not needed
    name_member.type.pack_packfile(item, value["name"], existing_items, data_pack_queue, pointer_size)

    class_name_member = hk_type.members[1]
    item.writer.pad_to_offset(member_start_offset + class_name_member.offset)
    _debug_print_pack(f"Member 'className' (type `{class_name_member.type.__name__}`):")
    class_name_member.type.pack_packfile(item, value["className"], existing_items, data_pack_queue, pointer_size)

    variant_member = hk_type.members[2]
    item.writer.pad_to_offset(member_start_offset + variant_member.offset)
    _debug_print_pack(f"Member 'variant' (type `{variant_member.type.__name__}`):")
    variant_member.type.pack_packfile(item, value["variant"], existing_items, data_pack_queue, pointer_size)

    _decrement_debug_indent()


def create_module_from_files(version="2015", *file_paths: str | Path, is_tagfile=True, module_path: Path = None):
    """Create an actual Python module with a real class hierarchy that fully captures Havok types."""
    if not file_paths:
        raise ValueError("At least one file path must be given to create Havok types module.")

    if module_path is None:
        module_path = Path(__file__).parent / f"hk{version}.py"

    module_str = f"\"\"\"Auto-generated types for Havok {version}.\n\nGenerated from files:"
    for file_path in file_paths:
        module_str += f"\n    {file_path.name}"
    module_str += "\n\"\"\"\nfrom __future__ import annotations\n\nfrom soulstruct_havok.types.core import *\n"

    # TODO: Detect if file is tag/pack, then open it, but extract `TypeInfo` list only. (Don't need any generic types.)
    #  Things to consider:
    #   - Only tagfiles have (and use) the "tag_format_flags" type attribute; it just indicates which other type
    #     attributes are present in the tagfile (as varints). These will need to be generated accurately if/when
    #     converting packfiles to tagfiles.

    # Next, we iterate over our types list, but we don't generate them in the random order in the XML. Instead, we use
    # `tag_type_flags` to load more primitive types first, then load classes afterwards.

    raw_type_infos = []  # type: list[TypeInfo]
    from soulstruct_havok.packfile.unpacker import PackFileUnpacker
    from soulstruct_havok.tagfile.unpacker import TagFileUnpacker
    for file_path in file_paths:
        # TODO: Detect tagfile vs. packfile.
        file_reader = BinaryReader(file_path)
        if is_tagfile:
            unpacker = TagFileUnpacker()
            unpacker.unpack(file_reader, compendium=None, types_only=True)
            raw_type_infos += unpacker.hk_type_infos[1:]  # skip `None` pad at index 0
        else:
            unpacker = PackFileUnpacker()
            unpacker.unpack(file_reader, types_only=True)
            raw_type_infos += unpacker.hk_type_infos  # skip `None` pad at index 0

    # Remove duplicate types (probably many).
    generic_types = {"hkArray", "hkEnum", "hkRefPtr", "hkRefVariant", "hkViewPtr", "T*", "T[N]"}
    type_info_dict = {}
    for type_info in raw_type_infos:
        if type_info.name in generic_types or type_info.py_name in type_info_dict:  # always skipped
            continue
        type_info_dict[type_info.py_name] = type_info

    defined_py_names = ["hk"]

    def define(_name: str, optional=False) -> str:
        if _name not in type_info_dict and optional:
            return ""
        _type_info = type_info_dict[_name]
        _py_name = _type_info.py_name
        if _py_name in defined_py_names:
            print(f"ALREADY DEFINED: {_py_name}")
            return ""
        class_str = "\n\n" + _type_info.get_class_py_def(defined_py_names)
        defined_py_names.append(_py_name)
        print(f"    BUILT: {_py_name}")
        return class_str

    def define_all(_names: list[str]):
        """Keep iterating over filtered type list, attempting to define them, until they can all be defined."""
        _names = [_name for _name in _names if _name not in defined_py_names]
        if not _names:
            return ""
        class_strs = []
        while True:
            new_definitions = []
            exceptions = []
            for _name in _names:
                _type_info = type_info_dict[_name]
                try:
                    class_str = define(_name)
                    class_strs.append(class_str)
                    new_definitions.append(_name)
                except TypeNotDefinedError as ex:
                    exceptions.append(f"{_name}: {str(ex)}")
                    continue  # try next type
            if not new_definitions:
                # Could not define anything on this pass. Raise all exceptions from this pass.
                ex_str = "\n    ".join(exceptions)
                print(f"Defined py names: {defined_py_names}")
                raise HavokTypeError(
                    f"Could not define any types remaining in list: {[_name for _name in _names]}.\n\n"
                    f"Last errors:\n    {ex_str}"
                )
            for _name in new_definitions:
                _names.remove(_name)
            if not _names:
                break
        return "".join(class_strs)

    print("Defining Invalid Types")

    module_str += f"\n\n# --- Invalid Types --- #\n"
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if type_info.tag_data_type == TagDataType.Invalid
    ])

    print("Defining Primitive Types")

    module_str += f"\n\n# --- Primitive Types --- #\n"
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if not any(type_info.name.startswith(s) for s in HAVOK_TYPE_PREFIXES)
    ])

    print("Defining Havok Struct Types")

    # Basic 'Struct' types.
    module_str += f"\n\n# --- Havok Struct Types --- #\n"
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if type_info.get_parent_value("tag_data_type") == TagDataType.Struct
    ])
    module_str += define("hkQsTransformf", optional=True)  # bundles other structs together
    module_str += define("hkQsTransform", optional=True)  # alias for above

    print("Defining Havok Wrappers")

    # Other shallow wrappers.
    module_str += f"\n\n# --- Havok Wrappers --- #\n"
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if type_info.tag_type_flags is None
    ])

    print("Defining Havok Core Types")

    # Core classes.
    module_str += f"\n\n# --- Havok Core Types --- #\n"
    module_str += define("hkBaseObject")
    # `hkReferencedObject` is left to its own devices, as in 2016 onwards, it has other `hkPropertyBag` dependencies.

    # Everything else.
    module_str += define_all([
        name for name, type_info in type_info_dict.items()
        if name not in defined_py_names
    ])

    with module_path.open("w") as f:
        f.write(module_str)


def create_2015_module():
    create_module_from_files(
        "2015",
        Path("../../tests/resources/DSR/c2240/Skeleton.HKX"),
        Path("../../tests/resources/DSR/c2240/c2240.hkx"),
        Path("../../tests/resources/DSR/c2240/a00_3000.hkx"),
        is_tagfile=True,
        module_path=Path(__file__).parent / f"hk2015_new.py"
    )


def create_2018_module():
    create_module_from_files(
        "2018",
        Path(r"C:\Dark Souls\c2180-anibnd-dcx\GR\data\INTERROOT_ps4\chr\c2180\hkx\skeleton.hkx"),
        Path(r"C:\Dark Souls\c2180-chrbnd-dcx\GR\data\INTERROOT_ps4\chr\c2180\c2180_c.hkx"),
        is_tagfile=True,
        module_path=Path(__file__).parent / f"hk2018.py"
    )


if __name__ == '__main__':
    create_2015_module()
    # create_2018_module()
