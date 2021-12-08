from __future__ import annotations

__all__ = [
    "DefType",
    "TemplateType",
    "TemplateValue",
    "Member",
    "Interface",
    "hk",
    "hkArray_",
    "hkArray",
    "hkStruct_",
    "hkStruct",
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
    "unpack_named_variant",
    "unpack_named_variant_packfile",
]

import typing as tp
from pathlib import Path

from soulstruct.utilities.binary import BinaryReader, BinaryWriter
from soulstruct.utilities.inspection import get_hex_repr

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.tagfile.structs import TagFileItem
from soulstruct_havok.types.info import *

if tp.TYPE_CHECKING:
    from soulstruct_havok.packfile.structs import PackFileItemEntry


_DEBUG_PRINT_UNPACK = False
_DEBUG_PRINT_PACK = False
_INDENT = 0
_REQUIRE_INPUT = False


def _debug_print_unpack(msg: str):
    global _INDENT
    if _DEBUG_PRINT_UNPACK:
        print(" " * _INDENT + msg)


def _debug_print_pack(msg: str):
    global _INDENT
    if _DEBUG_PRINT_PACK:
        print(" " * _INDENT + msg)


def _increment_debug_indent():
    global _INDENT
    _INDENT += 4


def _decrement_debug_indent():
    global _INDENT
    _INDENT -= 4


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
    name: str
    type: tp.Union[tp.Type[hk], DefType]
    offset: int
    flags: int


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

    @classmethod
    def get_member_names(cls):
        return [m.name for m in cls.members]

    @classmethod
    def get_tag_data_type(cls):
        return TagDataType(cls.tag_type_flags & 0xFF)

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-2])  # exclude `hk` and `object`

    @classmethod
    def unpack(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> tp.Any:
        """Unpack a `hk` instance from `reader`.

        Primitive types are converted to their Python equivalent, arrays are converted to list (in their overriding
        method), and so on. The types stored in the `hk` definition indicate how these Python values should be repacked
        by `pack()` below.
        """
        reader.seek(offset)
        _debug_print_unpack(f"Unpacking `{cls.__name__}`... ({cls.get_tag_data_type().name}) <{hex(offset)}>")
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
    def pack(cls, writer: BinaryWriter, value: tp.Any, items: list[TagFileItem], existing_items: dict[hk, TagFileItem]):
        """Use this `hk` type to process and pack the Python `value`.

        Primitive types and structs can be packed immediately, without creating a new item (whichever item the `writer`
        is currently in is correct). For types with members (Class types), any pointer, array, and string member types
        will cause a new item to be created with its own `BinaryWriter`; this item's data, once complete, will be stored
        in its `data` attribute, and all items' data can be assembled in order at the end.
        """
        _debug_print_pack(f"Packing `{cls.__name__}` with value {value}... ({cls.get_tag_data_type().name})")
        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot pack opaque type (and the file expects no data).
            pass
        elif tag_data_type == TagDataType.Bool:
            pack_bool(cls, writer, value)
        elif tag_data_type == TagDataType.String:
            pack_string(cls, writer, value, items)
        elif tag_data_type == TagDataType.Int:
            pack_int(cls, writer, value)
        elif tag_data_type == TagDataType.Float:
            pack_float(cls, writer, value)
        elif tag_data_type == TagDataType.Class:
            pack_class(cls, writer, value, items, existing_items)
        else:
            # 'Pointer' and 'Array' types are handled by `_Pointer` and `_hkArray` subclasses, respectively.
            raise ValueError(f"Cannot pack `hk` subclass `{cls.__name__}` with tag data type {tag_data_type}.")

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

        for member in cls.members:
            if member.name == "ptr":  # e.g. `hkRefVariant`
                # noinspection PyUnresolvedReferences
                type_info.pointer_type_py_name = member.type.get_data_type().__name__

        type_info.interfaces = [
            InterfaceInfo(interface.flags, type_py_name=interface.type.__name__)
            for interface in cls.get_interfaces()
        ]

        return type_info

    @classmethod
    def update_type_info_dict(cls, type_info_dict: dict[str, TypeInfo]) -> list[TypeInfo]:
        """Updates `type_info_dict` with the types needed by this Python class.

        Also returns a list of all new types created here (that is, types that were actually added to the dictionary).

        This base method only requires one corresponding type. Children like `_hkArray` and `_hkEnum` will create
        additional generic types in their overrides of this method.
        """
        if cls.__name__ in type_info_dict:
            return []
        new_type_info = cls.get_type_info()
        type_info_dict[cls.__name__] = new_type_info
        return [new_type_info]

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

    def collect_types_with_instance(self):
        return self.collect_types(self)

    @classmethod
    def collect_types(cls, instance=None) -> list[tp.Type[hk]]:
        """Collect all types used by all templates, interfaces, and members of this type, and so on, recursively.

        We use the type's `members` definition mostly, so we can return the full set of `hkArray`, `Pointer`, etc.
        classes, but need the actual instance to confirm the types used by any variant fields and parent-class pointers.

        This only returns the Python classes; index detection for writing needs to be done by the caller.

        NOTE: There are no "pointers to arrays" or "arrays of arrays" or "pointers to pointers", which simplifies things
        somewhat. There are just arrays of pointers sometimes.

        Also note that, to simplify the logic for primitive types that use primitive Python types like `int`, this type
        itself is not collected here, but should be handled by the caller instead.
        """
        all_types = []  # does NOT check own type

        for template_info in cls.get_templates():
            if isinstance(template_info, TemplateType):
                all_types.append(template_info.type)

        for interface_info in cls.get_interfaces():
            all_types.append(interface_info.type)

        for member_info in cls.members:

            member_value = getattr(instance, member_info.name) if instance else None

            if issubclass(member_info.type, hkArray_):
                all_types += member_info.type.get_type_hierarchy()  # `hkArray` type
                data_type = member_info.type.get_data_type()
                all_types += data_type.get_type_hierarchy()
                all_types += data_type.collect_types()
                if issubclass(data_type, Ptr_):
                    ptr_data_type = data_type.get_data_type()
                    if ptr_data_type != cls:
                        all_types += ptr_data_type.get_type_hierarchy()
                        all_types += ptr_data_type.collect_types()
                if issubclass(data_type, Ptr_) or data_type.members:
                    # Note that if this is an array of pointers, the pointer type has already been added, and the Python
                    # object will still just be a list of `hk` instances.
                    if member_value is not None:
                        member_value: list[hk]
                        for i, element in enumerate(member_value):
                            if element is not None:
                                all_types += type(element).get_type_hierarchy()
                                all_types += element.collect_types_with_instance()

            elif issubclass(member_info.type, hkStruct_):
                # Very similar to array.
                all_types += member_info.type.get_type_hierarchy()  # `hkStruct` type
                data_type = member_info.type.get_data_type()
                all_types += data_type.get_type_hierarchy()
                all_types += data_type.collect_types()
                if issubclass(data_type, Ptr_):
                    ptr_data_type = data_type.get_data_type()
                    if ptr_data_type != cls:
                        all_types += ptr_data_type.get_type_hierarchy()
                        all_types += ptr_data_type.collect_types()
                if issubclass(data_type, Ptr_) or data_type.members:
                    all_types += data_type.collect_types()
                    if member_value is not None:
                        member_value: tuple[hk]
                        for i, element in enumerate(member_value):
                            if element is not None:
                                all_types += type(element).get_type_hierarchy()
                                all_types += element.collect_types_with_instance()

            elif issubclass(member_info.type, Ptr_) or member_info.name == "ptr":  # includes `hkRefPtr`
                # Similar to above, but no iteration over elements required.
                all_types += member_info.type.get_type_hierarchy()  # `Ptr` type
                data_type = member_info.type.get_data_type()
                if data_type != cls:
                    all_types += data_type.get_type_hierarchy()  # Data type
                    all_types += data_type.collect_types()
                    if member_value is not None:
                        member_value: hk
                        all_types += type(member_value).get_type_hierarchy()  # type may be a subclass of expected
                        all_types += member_value.collect_types_with_instance()

            elif issubclass(member_info.type, hkEnum_):
                # Similar to above, but no iteration over elements required.
                all_types += member_info.type.get_type_hierarchy()  # `hkEnum` type
                all_types += member_info.type.enum_type.get_type_hierarchy()  # no need to collect

            elif member_info.type.get_tag_data_type() == TagDataType.Class:
                # Member value may be a subclass of class type.
                all_types += member_info.type.get_type_hierarchy()
                all_types += member_info.type.collect_types()
                if member_value is not None:
                    member_value: hk
                    all_types += type(member_value).get_type_hierarchy()  # type may be a subclass of expected
                    all_types += member_value.collect_types_with_instance()

            else:
                # Just a primitive type.
                all_types += member_info.type.get_type_hierarchy()
                all_types += member_info.type.collect_types()
                # No need to check member value.

        return all_types

    def get_tree_string(self, indent=0, instances_shown: list = None) -> str:
        """Recursively build indented string of this instance and everything within its members."""
        if instances_shown is None:
            instances_shown = []
        lines = [f"{self.__class__.__name__}("]
        for member in self.members:
            member_value = getattr(self, member.name)
            if member_value is None or isinstance(member_value, (bool, int, float, str)):
                lines.append(f"    {member.name} = {repr(member_value)}")
            elif isinstance(member_value, hk):
                if member_value in instances_shown:
                    lines.append(
                        f"    {member.name} = {member_value.__class__.__name__} "
                        f"<{instances_shown.index(member_value)}>")
                else:
                    lines.append(
                        f"    {member.name} = {member_value.get_tree_string(indent + 4, instances_shown)} "
                        f"<{len(instances_shown)}>"
                    )
                    instances_shown.append(member_value)
            elif isinstance(member_value, list):
                if not member_value:
                    lines.append(f"    {member.name} = []")
                elif isinstance(member_value[0], hk):
                    lines.append(f"    {member.name} = [")
                    for element in member_value:
                        if element in instances_shown:
                            lines.append(f"        {element.__class__.__name__} <{instances_shown.index(element)}>")
                        else:
                            element_string = element.get_tree_string(indent + 8, instances_shown)
                            lines.append(
                                f"        {element_string}, "
                                f"<{len(instances_shown)}>"
                            )
                            instances_shown.append(element)
                    lines.append(f"    ]")
                elif isinstance(member_value[0], (list, tuple)):
                    lines.append(f"    {member.name} = [")
                    for element in member_value:
                        lines.append(f"        {repr(element)},")
                    lines.append(f"    ]")
                else:
                    lines.append(f"    {member.name} = {repr(member_value)}")
            elif isinstance(member_value, tuple):
                if not member_value:
                    lines.append(f"    {member.name} = ()")
                elif isinstance(member_value[0], hk):
                    lines.append(f"    {member.name} = (")
                    for element in member_value:
                        if element in instances_shown:
                            lines.append(f"        {element.__class__.__name__} <{instances_shown.index(element)}>")
                        else:
                            lines.append(
                                f"        {element.get_tree_string(indent + 8, instances_shown)}, "
                                f"<{len(instances_shown)}>"
                            )
                            instances_shown.append(element)
                    lines.append(f"    )")
                elif isinstance(member_value[0], (list, tuple)):
                    lines.append(f"    {member.name} = (")
                    for element in member_value:
                        lines.append(f"        {repr(element)},")
                    lines.append(f"    )")
                else:
                    lines.append(f"    {member.name} = {repr(member_value)}")
            else:
                raise TypeError(f"Cannot parse value of member '{member.name}' for tree string: {type(member_value)}")
        lines.append(")")
        return f"\n{' ' * indent}".join(lines)

    def __repr__(self):
        return f"{type(self).__name__}()"


# --- GENERIC CLASS BASES & GENERATORS --- #


class hkArray_(hk):
    """Array base class, which is used to generate subclasses dynamically for different data types.

    The array template 'tT' is always a T* pointer to type `data_type`, and member `m_data` is a pointer to that pointer
    type (the first item in the array). These details aren't needed for actually unpacking and repacking data, though.

    Other hkArray properties, like `tAllocator` and `m_size`, are constant and can be automatically generated.
    """
    alignment = 8
    byte_size = 16
    tag_type_flags = 8

    __tag_format_flags = 43

    _data_type = None  # type: tp.Type[hk] | hkRefPtr | hkViewPtr | DefType

    @classmethod
    def get_data_type(cls):
        if isinstance(cls._data_type, DefType):
            cls._data_type = cls._data_type.action()
            return
        return cls._data_type

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
        writer: BinaryWriter,
        value: list[hk] | list[int] | list[float] | list[str] | list[bool],
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
    ):
        """Remember that array length can be variable, unlike `hkStruct`."""
        _debug_print_pack(f"Packing `{cls.__name__}`... (length = {len(value)})")
        pack_array(cls.get_data_type(), writer, value, items, existing_items)
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
    def update_type_info_dict(cls, type_info_dict: dict[str, TypeInfo]) -> list[TypeInfo]:
        """If needed, also creates pointer type for `hkArray` generic type to be packed."""
        if cls.__name__ in type_info_dict:
            return []
        new_types = []
        pointer_py_name = f"Ptr[{cls.get_data_type().__name__}]"
        if pointer_py_name not in type_info_dict:
            pointer_type_py_name = cls.get_data_type().__name__
            pointer_type_info = TypeInfo("T*")
            pointer_type_info.templates = [
                TemplateInfo("tT", type_py_name=pointer_type_py_name),
            ]
            pointer_type_info.pointer_type_py_name = pointer_type_py_name
            pointer_type_info.tag_format_flags = 11
            pointer_type_info.tag_type_flags = 6
            pointer_type_info.byte_size = 8
            pointer_type_info.alignment = 8
            type_info_dict[pointer_py_name] = pointer_type_info
            new_types.append(pointer_type_info)
        array_type_info = cls.get_type_info()
        type_info_dict[cls.__name__] = array_type_info
        new_types.append(array_type_info)
        return new_types

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-3])  # exclude this, `hk`, and `object`


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
    def pack(cls, writer: BinaryWriter, value: tp.Any, items: list[TagFileItem], existing_items: dict[hk, TagFileItem]):
        return cls.storage_type.pack(writer, value, items, existing_items)

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
    def update_type_info_dict(cls, type_info_dict: dict[str, TypeInfo]) -> list[TypeInfo]:
        """If needed, also creates named enum type used as 'tENUM' template by generic `hkEnum` type.
        """
        if cls.__name__ in type_info_dict:
            return []
        new_types = []

        # Both `tENUM` and `tSTORAGE` types will be real defined types, so it's just down to chance if they've already
        # been defined by the time we get here, most likely (as they will be collected alongside this wrapper).

        enum_py_name = cls.enum_type.__name__
        if enum_py_name not in type_info_dict:
            enum_type_info = cls.enum_type.get_type_info()
            type_info_dict[enum_py_name] = enum_type_info
            new_types.append(enum_type_info)

        storage_py_name = cls.storage_type.__name__
        if storage_py_name not in type_info_dict:
            storage_type_info = cls.storage_type.get_type_info()
            type_info_dict[storage_py_name] = storage_type_info
            new_types.append(storage_type_info)

        generic_enum_type_info = cls.get_type_info()
        type_info_dict[cls.__name__] = generic_enum_type_info
        new_types.append(generic_enum_type_info)
        return new_types

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


class hkStruct_(hk):
    """Simple wrapper type for both 'T[N]' types and built-in tuple types like `hkVector4f`.

    These types store a fixed amount of data locally (e.g., within the same item) rather than separately, like arrays.
    """
    _data_type = None  # type: tp.Type[hk] | DefType  # no `DefType()` instances, I believe
    length = 0
    is_generic = False

    @classmethod
    def get_data_type(cls) -> tp.Type[hk]:
        """I don't believe self-references ever appear in Structs, but just in case (and for consistency)."""
        if isinstance(cls._data_type, DefType):
            cls._data_type = cls._data_type.action()
        return cls._data_type

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
    def pack(cls, writer: BinaryWriter, value: tp.Any, items: list[TagFileItem], existing_items: dict[hk, TagFileItem]):
        pack_struct(cls.get_data_type(), writer, value, items, existing_items, cls.length)

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
            type_info.tag_type_flags = cls.tag_type_flags  # already set to correct subtype
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

    # Uses standard `update_type_info_dict()`, as no additional generic types need to be created.

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        if cls.is_generic:
            # noinspection PyTypeChecker
            return list(cls.__mro__[:-3])  # exclude this, `hk`, and `object`
        else:
            # noinspection PyTypeChecker
            return list(cls.__mro__[:-4])  # exclude `_hkStruct[type, length]` subclass, this, `hk`, and `object`


def hkStruct(
    data_type: tp.Type[hk], length: int, generic_tag_subtype: TagDataType = None
) -> tp.Type[hkStruct_]:
    """Generates a `_hkStruct` subclass dynamically.

    Needs all the basic `hk` information, unfortunately, as it can vary (except `tag_format_flags`, which is always 11).
    """
    # noinspection PyTypeChecker
    struct_type = type(f"hkStruct[{data_type.__name__}, {length}]", (hkStruct_,), {})  # type: tp.Type[hkStruct_]
    if generic_tag_subtype:
        struct_type.tag_type_flags = TagDataType.Struct | generic_tag_subtype
        struct_type.is_generic = True
    else:
        struct_type.is_generic = False
    struct_type._data_type = data_type
    struct_type.length = length
    return struct_type


class Ptr_(hk):
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

    _data_type = None  # type: tp.Type[hk] | DefType

    @classmethod
    def get_data_type(cls):
        if isinstance(cls._data_type, DefType):
            cls._data_type = cls._data_type.action()
        return cls._data_type

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
        writer: BinaryWriter,
        value: hk,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem] = None,
    ):
        _debug_print_pack(f"Packing `{cls.__name__}`...")
        pack_pointer(cls.get_data_type(), writer, value, items, existing_items)
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

    # Uses standard `update_type_info_dict()`, as no additional generic types need to be created.

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-3])  # exclude this, `hk`, and `object`


def Ptr(data_type: tp.Type[hk] | DefType, hsh: int = None) -> tp.Type[Ptr_]:
    """Create a `_Ptr` subclass dynamically, pointing to a particular type."""
    data_type_name = data_type.type_name if isinstance(data_type, DefType) else data_type.__name__
    # noinspection PyTypeChecker
    ptr_type = type(f"Ptr[{data_type_name}]", (Ptr_,), {})  # type: tp.Type[Ptr_]
    ptr_type._data_type = data_type
    ptr_type.__hsh = hsh
    return ptr_type


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
        return list(cls.__mro__[:-4])  # exclude this, `_Ptr`, `hk`, and `object`

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

    @classmethod
    def update_type_info_dict(cls, type_info_dict: dict[str, TypeInfo]) -> list[TypeInfo]:
        """If needed, also creates pointer type for `hkRefPtr[ptr]` generic type member to be packed."""
        if cls.__name__ in type_info_dict:
            return []
        new_types = []
        pointer_py_name = f"Ptr[{cls.get_data_type().__name__}]"
        if pointer_py_name not in type_info_dict:
            data_type_py_name = cls.get_data_type().__name__
            pointer_type_info = TypeInfo("T*")
            pointer_type_info.templates = [
                TemplateInfo("tT", type_py_name=data_type_py_name),
            ]
            pointer_type_info.pointer_type_py_name = data_type_py_name
            pointer_type_info.tag_format_flags = 11
            pointer_type_info.tag_type_flags = 6
            pointer_type_info.byte_size = 8
            pointer_type_info.alignment = 8
            type_info_dict[pointer_py_name] = pointer_type_info
            new_types.append(pointer_type_info)
        ref_ptr_type_info = cls.get_type_info()
        type_info_dict[cls.__name__] = ref_ptr_type_info
        new_types.append(ref_ptr_type_info)
        return new_types


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
        return list(cls.__mro__[:-4])  # exclude this, `Ptr_`, `hk`, and `object`

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

    @classmethod
    def update_type_info_dict(cls, type_info_dict: dict[str, TypeInfo]) -> list[TypeInfo]:
        """If needed, also creates pointer type for `hkRefVariant[ptr]` generic type member to be packed."""
        if cls.__name__ in type_info_dict:
            return []
        new_types = []
        pointer_py_name = f"Ptr[{cls.get_data_type().__name__}]"
        if pointer_py_name not in type_info_dict:
            data_type_py_name = cls.get_data_type().__name__
            pointer_type_info = TypeInfo("T*")
            pointer_type_info.templates = [
                TemplateInfo("tT", type_py_name=data_type_py_name),
            ]
            pointer_type_info.pointer_type_py_name = data_type_py_name
            pointer_type_info.tag_format_flags = 11
            pointer_type_info.tag_type_flags = 6
            pointer_type_info.byte_size = 8
            pointer_type_info.alignment = 8
            type_info_dict[pointer_py_name] = pointer_type_info
            new_types.append(pointer_type_info)
        ref_variant_type_info = cls.get_type_info()
        type_info_dict[cls.__name__] = ref_variant_type_info
        new_types.append(ref_variant_type_info)
        return new_types


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

    @classmethod
    def update_type_info_dict(cls, type_info_dict: dict[str, TypeInfo]) -> list[TypeInfo]:
        """If needed, also creates pointer type for `hkViewPtr[ptr]` generic type member to be packed."""
        if cls.__name__ in type_info_dict:
            return []
        new_types = []
        pointer_py_name = f"Ptr[{cls.data_type_name}]"
        if pointer_py_name not in type_info_dict:
            pointer_type_info = TypeInfo("T*")
            pointer_type_info.templates = [
                TemplateInfo("tT", type_py_name=cls.data_type_name),
            ]
            pointer_type_info.pointer_type_py_name = cls.data_type_name
            pointer_type_info.tag_format_flags = 11
            pointer_type_info.tag_type_flags = 6
            pointer_type_info.byte_size = 8
            pointer_type_info.alignment = 8
            # `hkViewPtr` hash is actually its pointer's hash.
            pointer_type_info.hsh = cls.__dict__["__hsh"]
            type_info_dict[pointer_py_name] = pointer_type_info
            new_types.append(pointer_type_info)
        view_ptr_type_info = cls.get_type_info()
        type_info_dict[cls.__name__] = view_ptr_type_info
        new_types.append(view_ptr_type_info)
        return new_types


def hkViewPtr(data_type_name: str, hsh: int = None):
    """Create a `_hkViewPtr` subclass dynamically, pointing to a particular type name."""
    # noinspection PyTypeChecker
    ptr_type = type(f"hkViewPtr[{data_type_name}]", (hkViewPtr_,), {})  # type: tp.Type[hkViewPtr_]
    ptr_type.data_type_name = data_type_name
    ptr_type.__hsh = hsh
    return ptr_type


class NewStruct_(hk):
    """Wrapper for a new type of pointer that only appears in `hknp` classes. (Name chosen by me.)

    It reads `length` and `jump` shorts, and uses that offset to make a jump ahead (from just before `length`) to
    tightly packed struct value of some data type, which is unpacked into a tuple.
    """
    # TODO: No idea what these values should be (except `byte_size = 4`).
    alignment = 4
    byte_size = 4
    tag_type_flags = 6

    __tag_format_flags = 11

    _data_type = None  # type: tp.Type[hk] | DefType

    @classmethod
    def get_data_type(cls):
        if isinstance(cls._data_type, DefType):
            cls._data_type = cls._data_type.action()
        return cls._data_type

    @classmethod
    def set_data_type(cls, data_type: tp.Type[hk]):
        cls._data_type = data_type

    @classmethod
    def unpack(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> hk:
        raise TypeError("Have not encountered `JumpPtr` types in tagfiles before. Cannot unpack them.")

    @classmethod
    def unpack_packfile(cls, entry: PackFileItemEntry, offset: int = None, pointer_size=8):
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
        writer: BinaryWriter,
        value: hk,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem] = None,
    ):
        _debug_print_pack(f"Packing `{cls.__name__}`...")
        pack_pointer(cls.get_data_type(), writer, value, items, existing_items)
        if _REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        raise TypeError("Cannot convert `_NewStruct` to `TypeInfo` yet for packing packfiles.")

    # Uses standard `update_type_info_dict()`, as no additional generic types need to be created.

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-3])  # exclude this, `hk`, and `object`


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


def pack_bool(hk_type: tp.Type[hk], writer: BinaryWriter, value: bool):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    writer.pack(fmt, int(value))


def unpack_int(hk_type: tp.Type[hk], reader: BinaryReader) -> int:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt)


def pack_int(hk_type: tp.Type[hk], writer: BinaryWriter, value: int):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags, signed=value < 0)
    writer.pack(fmt, value)


def unpack_float32(reader: BinaryReader) -> float | hk:
    """32-bit floats are unpacked directly; others (like half floats) are unpacked as classes (Havok's setup)."""
    return reader.unpack_value("<f")


def pack_float(hk_type: tp.Type[hk], writer: BinaryWriter, value: float | hk):
    if hk_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
        writer.pack("<f", value)
    else:
        pack_class(hk_type, writer, value, items=[], existing_items={})  # will not use items


def unpack_class(
    hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem], instance=None
) -> hk:
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
    writer: BinaryWriter,
    value: hk,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
):
    member_start_offset = writer.position

    _increment_debug_indent()
    for member in hk_type.members:
        _debug_print_pack(f"Member '{member.name}' (type `{member.type.__name__}`):")
        # Member offsets may not be perfectly packed together, so we always pad up to the proper offset.
        writer.pad_to_offset(member_start_offset + member.offset)
        member.type.pack(writer, value[member.name], items, existing_items)
    _decrement_debug_indent()


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


def unpack_pointer_packfile(data_hk_type: tp.Type[hk], entry: PackFileItemEntry, pointer_size: int) -> hk | None:
    """`data_hk_type` is used to make sure that the referenced entry's `hk_type` is a subclass of it."""
    source_offset = entry.reader.position
    zero = entry.reader.unpack_value("<I" if pointer_size == 4 else "<Q")  # "dummy" pointer
    try:
        ref_entry, ref_data_offset = entry.entry_pointers[source_offset]
    except KeyError:
        if zero != 0:
            print(entry.entry_pointers)
            raise ValueError(
                f"Could not find entry pointer: type {entry.hk_type.__name__}, buffer at {hex(source_offset)}."
            )
        else:
            return None
    if zero != 0:
        raise AssertionError(f"Found non-zero data at entry pointer offset: {zero}.")
    if ref_data_offset != 0:
        print(entry.entry_pointers)
        raise AssertionError(f"Data entry pointer (global ref dest) was not zero: {ref_data_offset}.")
    if not issubclass(ref_entry.hk_type, data_hk_type):
        raise ValueError(
            f"Pointer-referenced entry type {ref_entry.hk_type.__name__} is not a child of expected type "
            f"{data_hk_type.__name__}."
        )
    if ref_entry.value is None:
        # Unpack entry (first time).
        ref_entry.start_reader()
        _increment_debug_indent()
        # NOTE: `ref_entry.hk_type` may be a subclass of `data_hk_type`, so it's important we use it here.
        ref_entry.value = ref_entry.hk_type.unpack_packfile(ref_entry, pointer_size=pointer_size)
        _decrement_debug_indent()
    else:
        _debug_print_unpack(f"Existing item: {type(ref_entry.value).__name__}")
    return ref_entry.value


def pack_pointer(
    data_hk_type: tp.Type[hk],
    writer: BinaryWriter,
    value: hk,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
):
    if value is None:
        writer.pack("<I", 0)
        return

    if value in existing_items:
        writer.pack("<I", items.index(existing_items[value]))
        return

    if not isinstance(value, data_hk_type):
        raise TypeError(
            f"Pointer to `{data_hk_type.__name__}` contained wrong type: `{value.__class__.__name__}`"
        )
    value_data_hk_type = type(value)

    writer.pack("<I", len(items))  # next index
    new_item = TagFileItem(value_data_hk_type, is_ptr=issubclass(value_data_hk_type, Ptr_))
    existing_items[value] = new_item
    items.append(new_item)
    new_item_writer = BinaryWriter()
    value_data_hk_type.pack(new_item_writer, value, items, existing_items)
    new_item.data = new_item_writer.finish()


def unpack_array(data_hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem]) -> list:
    item_index = reader.unpack_value("<I")
    _debug_print_unpack(f"Array item index: {item_index} (type `{data_hk_type.__name__}`)")
    if item_index == 0:
        return []
    item = items[item_index]
    # TODO: Shouldn't we use `item.hk_type`, not `data_hk_type` (which must only be a parent)?

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
        print(f"Entry entry pointers: {entry.entry_pointers}")
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
    data_hk_type: tp.Type[hk],
    writer: BinaryWriter,
    value: list[hk | str | int | float | bool],
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
):
    """Array items are always created per instance, never re-used. (Not sure if that's correct, but it is here.)"""
    if not value:
        writer.pack("<I", 0)
        return

    writer.pack("<I", len(items))  # next index
    new_item = TagFileItem(data_hk_type, is_ptr=issubclass(data_hk_type, Ptr_), length=len(value))
    items.append(new_item)
    new_item_writer = BinaryWriter()

    for i, element in enumerate(value):
        # TODO: Could validate element type here (for pointers/strings, at least).
        new_item_writer.pad_to_offset(i * data_hk_type.byte_size)
        data_hk_type.pack(new_item_writer, element, items, existing_items)

    new_item.data = new_item_writer.finish()


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
    writer: BinaryWriter,
    value: tuple,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    length: int,
):
    """Structs are packed locally in the same item, but can contain pointers themselves."""
    struct_start_offset = writer.position
    if len(value) != length:
        raise ValueError(f"Length of `{data_hk_type.__name__}` value is not {length}: {value}")
    for i, element in enumerate(value):
        writer.pad_to_offset(struct_start_offset + i * data_hk_type.byte_size)
        data_hk_type.pack(writer, element, items, existing_items)


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


def pack_string(string_hk_type: tp.Type[hk], writer: BinaryWriter, value: str, items: list[TagFileItem]):
    if not value:
        writer.pack("<I", 0)
        return
    if not isinstance(value, str):
        raise ValueError(f"Cannot pack non-string: {value}")

    writer.pack("<I", len(items))  # next index
    encoded = value.encode("shift_jis_2004") + b"\0"
    new_item = TagFileItem(string_hk_type, is_ptr=False, data=encoded, length=len(encoded))
    items.append(new_item)


def unpack_named_variant(
    hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem], types_module: dict
) -> hk:
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
    variant_py_name = variant_type_name.replace(" ", "_").replace("*", "").replace("::", "")
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
    variant_py_name = variant_type_name.replace(" ", "_").replace("*", "").replace("::", "")
    variant_type = types_module[variant_py_name]
    entry.reader.seek(member_start_offset + variant_member.offset)
    _debug_print_unpack(f"Unpacking named variant: {hk_type.__name__}... <{entry.reader.position_hex}>")
    _increment_debug_indent()
    variant_instance = unpack_pointer_packfile(variant_type, entry, pointer_size=pointer_size)
    _decrement_debug_indent()
    _debug_print_unpack(f"--> {variant_instance}")
    setattr(instance, variant_member.name, variant_instance)
    return instance


def create_module_from_files(version="2015", *file_paths: str | Path, is_tagfile=True):
    """Create an actual Python module with a real class hierarchy that fully captures Havok types."""
    module_path = Path(__file__).parent / f"hk{version}.py"

    module_str = ""

    # First, some very primitive types.
    module_str += f"""\"\"\"Auto-generated types for Havok {version}.

Generated from files:
"""
    for file_path in file_paths:
        module_str += f"    {file_path.name}\n"

    module_str += """
\"\"\"
from __future__ import annotations
import typing as tp

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.types.core import *

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.tagfile.structs import TagFileItem
    from soulstruct_havok.packfile.structs import PackFileItemEntry
"""
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

    def define(_type_info: TypeInfo):
        _py_name = _type_info.py_name
        if _py_name in defined_py_names:
            return ""
        class_str = "\n\n" + _type_info.get_py_class_def(defined_py_names)
        defined_py_names.append(_py_name)
        return class_str

    def define_all(_type_infos: list[TypeInfo]):
        """Keep iterating over filtered type list, attempting to define them, until they can all be defined."""
        if not _type_infos:
            return ""
        class_str = ""
        while True:
            new_definitions = []
            exceptions = []
            for _type_info in _type_infos:
                try:
                    class_str += define(_type_info)
                    new_definitions.append(_type_info)
                except TypeNotDefinedError as ex:
                    exceptions.append(str(ex))
                    continue  # try next type
            if not new_definitions:
                ex_str = "\n    ".join(exceptions)
                raise ValueError(
                    f"Could not define any types remaining in list: {[_t.name for _t in _type_infos]}.\n\n"
                    f"Last errors:\n    {ex_str}"
                )
            for _type_info in new_definitions:
                _type_infos.remove(_type_info)
            if not _type_infos:
                break
        return class_str

    module_str += f"\n\n# --- Invalid Types --- #\n"
    module_str += define_all([
        type_info for name, type_info in type_info_dict.items()
        if type_info.tag_data_type == TagDataType.Invalid
    ])

    module_str += f"\n\n# --- Primitive Types --- #\n"
    module_str += define_all([
        type_info for name, type_info in type_info_dict.items()
        if not type_info.name.startswith("hk")
    ])

    # Basic 'Struct' types.
    module_str += f"\n\n# --- Havok Struct Types --- #\n"
    module_str += define_all([
        type_info for name, type_info in type_info_dict.items()
        if type_info.get_parent_value("tag_data_type") == TagDataType.Struct
    ])
    module_str += define(type_info_dict["hkQsTransformf"])  # bundles other structs together
    module_str += define(type_info_dict["hkQsTransform"])  # alias for above

    # Other shallow wrappers.
    module_str += f"\n\n# --- Havok Wrappers --- #\n"
    module_str += define_all([
        type_info for name, type_info in type_info_dict.items()
        if type_info.tag_type_flags is None
    ])

    # Core classes.
    module_str += f"\n\n# --- Havok Core Types --- #\n"
    module_str += define(type_info_dict["hkBaseObject"])
    module_str += define(type_info_dict["hkReferencedObject"])

    # Everything else.
    module_str += define_all([
        type_info for name, type_info in type_info_dict.items()
        if name not in defined_py_names
    ])

    with module_path.open("w") as f:
        f.write(module_str)


if __name__ == '__main__':
    create_module_from_files(
        "2014",
        Path("../../tests/resources/BB/c2800/c2800.hkx").resolve(),
        is_tagfile=False,
    )

    # create_module_from_files(
    #     "2015",
    #     # Path("../../tests/resources/DSR/c2240/Skeleton.HKX").resolve(),
    #     Path("../../tests/resources/DSR/c2240/c2240.hkx").resolve(),
    #     # Path("../../tests/resources/DSR/c2240/a00_3000.hkx").resolve(),
    # )
