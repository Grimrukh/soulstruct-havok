from __future__ import annotations

__all__ = [
    "hk",
    "HK_TYPE",
    "TemplateType",
    "TemplateValue",
    "Member",
    "Interface",
    "DefType",
]

import copy
import inspect
import typing as tp
from contextlib import contextmanager
from dataclasses import dataclass

import colorama
import numpy as np

from soulstruct.utilities.binary import BinaryReader, BinaryWriter

from soulstruct_havok.enums import TagDataType, MemberFlags
from soulstruct_havok.packfile.structs import PackItemCreationQueues
from soulstruct_havok.tagfile.structs import TagItemCreationQueues, TagFileItem
from soulstruct_havok.types.info import *
from soulstruct_havok.utilities.maths import Quaternion, Vector4

from . import packfile, tagfile, debug


if tp.TYPE_CHECKING:
    from soulstruct_havok.packfile.structs import PackFileDataItem

colorama.just_fix_windows_console()
CYAN = colorama.Fore.CYAN
RESET = colorama.Fore.RESET


# region Supporting Types

@dataclass(slots=True)
class TemplateType:
    """Container for 't' templates."""
    name: str
    _type: type[hk] | DefType

    def get_type(self) -> type[hk]:
        """Resolve deferred type, if necessary."""
        if isinstance(self._type, DefType):
            self._type = self._type.action()
        return self._type


class TemplateValue(tp.NamedTuple):
    """Container for 'v' templates."""
    name: str
    value: int


class Member(tp.NamedTuple):
    """Simple container for member information."""
    offset: int
    name: str
    type: tp.Union[tp.Type[hk], DefType]
    extra_flags: int = 0  # in addition to `MemberFlags.Default`

    @property
    def py_name(self) -> str:
        """Adds an underscore prefix if `name` is not a valid Python identifier."""
        return f"_{self.name}" if self.name[0].isdigit() else self.name


class Interface(tp.NamedTuple):
    """Container for interface information."""
    type: tp.Type[hk]
    flags: int


class DefType:

    def __init__(self, type_name: str, action: tp.Callable[[], type[hk]]):
        """Deferred reference to own class (before Python has finished defining it).

        `action` will be used to set the attribute the first time it is accessed.
        """
        self.type_name = type_name
        self.action = action

    def get_type_name(self):
        """Mimics method of `hk`."""
        return self.type_name

# endregion


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hk:
    """Absolute base of every Havok type."""

    # Set before unpacking root and removed afterward, as `hkRootLevelContainerNamedVariant` objects need to dynamically
    # retrieve all type names.
    _TYPES_DICT: tp.ClassVar[dict[str, type[hk]] | None] = None

    alignment: tp.ClassVar[int] = 0
    byte_size: tp.ClassVar[int] = 0
    tag_type_flags: tp.ClassVar[int] = 0
    _tag_data_type: tp.ClassVar[TagDataType] = None  # cached on first call of `get_tag_data_type()`

    # This field is used by tagfiles to indicate which of these other attributes should be read/written.
    __tag_format_flags: tp.ClassVar[int] = 0

    # These fields are optional (defaulting to `None`), not inherited (hence the double underscore), and have class
    # methods for getting and setting.
    __hsh: tp.ClassVar[int | None] = None  # only used by some types
    __abstract_value: tp.ClassVar[int | None] = None  # only used by some 'Class' types
    __version: tp.ClassVar[int | None] = None  # only used by some 'Class' types

    __real_name: tp.ClassVar[str] = ""  # if different to type (e.g. colons, asterisk, or clashes with a Python type)

    local_members: tp.ClassVar[tuple[Member, ...]] = ()  # only members added by this class
    members: tp.ClassVar[tuple[Member, ...]] = ()  # includes all parent class members

    # We only care about local, mangled templates/interfaces, since they are never used in unpacking.
    # NOTE: I don't think it's possible for a type with templates/interfaces to be subclassed (with ADDITIONAL templates
    # or interfaces, at least), but these are mangled just to be safe.
    __templates: tp.ClassVar[tuple[TemplateValue | TemplateType, ...]] = ()
    __interfaces: tp.ClassVar[tuple[TemplateValue | TemplateType, ...]] = ()
    
    # No instance variables in this base class. All defined by subclasses.

    def copy(self):
        """Make a deep copy of this `hk` instance by calling `copy()` on `hk`-type members and built-in `deepcopy()` on
        primitive-type members."""
        self_copy = self.__class__()
        for member_name in self.get_member_names():
            member_value = getattr(self, member_name)
            if isinstance(member_value, hk):  # recur on member data `hk.copy()`
                setattr(self_copy, member_name, member_value.copy())
            else:  # primitive Python type
                setattr(self_copy, member_name, copy.deepcopy(member_value))

    @classmethod
    def get_default_value(cls):
        """Specify some basic default values for primitive types.

        `hk` subclasses may override this to provide their own defaults.
        """
        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            return None
        elif tag_data_type == TagDataType.Bool:
            return False
        elif tag_data_type in {TagDataType.CharArray, TagDataType.ConstCharArray}:
            return ""
        elif tag_data_type == TagDataType.Int:
            return 0
        elif tag_data_type == TagDataType.Float:
            return 0.0
        elif tag_data_type == TagDataType.Class:
            return None
        else:
            raise ValueError(f"Type `{cls.__name__}` has no default value available.")

    @classmethod
    def get_type_name(cls, lstrip_underscore=False):
        """Easier way (especially for instances) to get Python class name."""
        if lstrip_underscore:
            return cls.__name__.lstrip("_")
        return cls.__name__

    @classmethod
    def get_member_names(cls):
        return [m.name for m in cls.members]

    @classmethod
    def get_type_with_member(cls, member_name: str) -> type[hk]:
        """Find the Havok type in this class's hierarchy that actually defines the given `member_name`."""
        for parent_type in cls.get_type_hierarchy():
            if member_name in [m.name for m in parent_type.local_members]:
                return parent_type
        raise ValueError(f"Member '{member_name}' is not defined by any base type of {cls.get_type_name()}.")

    @classmethod
    def get_tag_data_type(cls):
        """Lowest eight bits of `tag_type_flags`. Cached on first access."""
        if cls._tag_data_type is None:
            cls._tag_data_type = TagDataType(cls.tag_type_flags & 0b1111_1111)
        return cls._tag_data_type

    @classmethod
    def get_type_hierarchy(cls) -> list[type[hk]]:
        return list(cls.__mro__[:-2])  # exclude `hk` and `object`

    @classmethod
    def get_immediate_parent(cls) -> tp.Optional[type[hk]]:
        """Get immediate `hk` parent if one exists."""
        hierarchy = cls.get_type_hierarchy()
        if len(hierarchy) > 1:
            return hierarchy[1]
        return None

    @classmethod
    def get_alignment(cls, long_varints: bool):
        """Get alignment for this type, considering `long_varints` setting when alignment is -1 (pointers)."""
        if cls.alignment == -1:
            return 8 if long_varints else 4
        return cls.alignment

    @classmethod
    def get_byte_size(cls, long_varints: bool):
        """Get byte size for this type, considering `long_varints` setting when size is -1 (pointers)."""
        if cls.byte_size == -1:
            return 8 if long_varints else 4
        return cls.byte_size

    @staticmethod
    @contextmanager
    def set_types_dict(module):
        """Assign `soulstruct_havok.types.hkXXXX` submodule to `hk` so that dynamic type names can be resolved (e.g.,
        `hkRootLevelContainerNamedVariant`, `hkViewPtr`).

        Should be used via `with` context to ensure the dictionary is unassigned when unpacking is finished. Not
        required for packing because the types are already assigned.
        """
        hk._TYPES_DICT = {
            name: hk_type
            for name, hk_type in inspect.getmembers(module, lambda x: inspect.isclass(x) and issubclass(x, hk))
        }
        try:
            yield
        finally:
            hk._TYPES_DICT = None

    @classmethod
    def get_module_type(cls, type_name: str) -> type[hk]:
        if cls._TYPES_DICT is None:
            raise AttributeError(f"`hk.set_types_dict()` has not been called. Cannot retrieve type `{type_name}`.")
        return cls._TYPES_DICT[type_name]

    @classmethod
    def get_empty_instance(cls) -> tp.Self:
        """`hk` dataclasses normally do not have any default values, but this method will return an instance with all
        dataclass fields set to `None`. This is required for unpacking some items that recursively reference themselves,
        as we need to create the item instance before reading its members.
        """
        # noinspection PyArgumentList
        return cls(**{m.name: None for m in cls.members})

    @classmethod
    def unpack_tagfile(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> tp.Any:
        """Unpack a `hk` instance from `reader` for a newer Havok tagfile.

        Primitive types are converted to their Python equivalent, arrays are converted to list (in their overriding
        method), and so on. The types stored in the `hk` definition indicate how these Python values should be repacked
        by `pack()` below.
        """
        reader.seek(offset)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... ({cls.get_tag_data_type().name}) <{hex(offset)}>")

        if cls.__name__ == "hkRootLevelContainerNamedVariant":
            # Retrieve other classes from subclass's module, as they will be dynamically attached to the root container.
            if hk._TYPES_DICT is None:
                raise AttributeError(
                    "Cannot unpack `hkRootLevelContainerNamedVariant` without using types context manager."
                )
            return tagfile.unpack_named_variant(cls, reader, items, hk._TYPES_DICT)

        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot unpack opaque type (and there shouldn't be anything to unpack in the file).
            value = None
        elif tag_data_type == TagDataType.Bool:
            value = tagfile.unpack_bool(cls, reader)
        elif tag_data_type in {TagDataType.CharArray, TagDataType.ConstCharArray}:
            value = tagfile.unpack_string(reader, items)  # `cls` not needed
        elif tag_data_type == TagDataType.Int:
            value = tagfile.unpack_int(cls, reader)
        elif cls.tag_type_flags == TagDataType.FloatAndFloat32:
            value = tagfile.unpack_float32(reader)  # `cls` not needed
        elif tag_data_type in {TagDataType.Class, TagDataType.Float}:  # non-32-bit floats have members
            value = tagfile.unpack_class(cls, reader, items)
        elif tag_data_type == TagDataType.Array and cls.__name__ in {"hkPropertyBag", "hkReflectAny"}:
            # TODO: These two newer types are marked as Arrays, for some reason.
            #  Probably indicates that 'Array' actually means some kind of 'Pointer'?
            value = tagfile.unpack_class(cls, reader, items)
        else:
            # Note that 'Pointer', 'Array', and 'Struct' types have their own explicit subclasses.
            raise ValueError(f"Cannot unpack `hk` subclass `{cls.__name__}` with tag data type {tag_data_type.name}.")

        if debug.DEBUG_PRINT_UNPACK:
            if isinstance(value, list) and len(value) > 10 and isinstance(value[0], (int, float)):
                debug.debug_print(f"= {repr(value[:10])}... ({len(value)} elements)")
            else:
                debug.debug_print(f"= {repr(value)}")

        return value

    @classmethod
    def unpack_packfile(cls, item: PackFileDataItem, offset: int = None):
        """Unpack Python data from a Havok packfile.

        If `offset` is None, the `item.reader` continues from its current position.

        `item` already contains resolved pointers to other items, so no item list needs to be passed around.
        """
        item.reader.seek(offset) if offset is not None else item.reader.position

        if cls.__name__ == "hkRootLevelContainerNamedVariant":
            # Retrieve other classes from subclass's module, as they will be dynamically attached to the root container.
            if hk._TYPES_DICT is None:
                raise AttributeError(
                    "Cannot unpack `hkRootLevelContainerNamedVariant` without using types context manager."
                )
            return packfile.unpack_named_variant(cls, item, hk._TYPES_DICT)

        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot unpack opaque type (and there shouldn't be anything to unpack in the file).
            value = None
        elif tag_data_type == TagDataType.Bool:
            value = packfile.unpack_bool(cls, item.reader)
        elif tag_data_type in {TagDataType.CharArray, TagDataType.ConstCharArray}:
            value = packfile.unpack_string(item)  # `cls` not needed
        elif tag_data_type == TagDataType.Int:
            value = packfile.unpack_int(cls, item.reader)
        elif cls.tag_type_flags == TagDataType.FloatAndFloat32:
            value = packfile.unpack_float32(item.reader)  # `cls` not needed
        elif tag_data_type in {TagDataType.Class, TagDataType.Float}:  # non-32-bit floats have members (`value`)
            value = packfile.unpack_class(cls, item)
        else:
            # Note that 'Pointer', 'Array', and 'Struct' types have their own explicit subclasses.
            raise ValueError(f"Cannot unpack `hk` subclass `{cls.__name__}` with tag data type {tag_data_type}.")

        # if (
        #     debug.DEBUG_PRINT_UNPACK
        #     and not debug.DO_NOT_DEBUG_PRINT_PRIMITIVES
        #     and cls.__name__ not in {"_float", "hkUint8"}
        # ):
        #     if isinstance(value, np.ndarray) and value.size > 10:
        #         debug.debug_print(f"= {repr(value[:10])}... ({value.size} elements/rows)")
        #     elif isinstance(value, list) and len(value) > 10 and isinstance(value[0], (int, float)):
        #         debug.debug_print(f"= {repr(value[:10])}... ({len(value)} total)")
        #     else:
        #         debug.debug_print(f"= {repr(value)}")

        return value

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: tp.Any,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queues: TagItemCreationQueues = None,
    ):
        """Use this `hk` type to process and pack the Python `value`.

        Primitive types and structs can be packed immediately, without creating a new item (whichever item the `writer`
        is currently in is correct). For types with members (Class types), any pointer, array, and string member types
        will cause a new item to be created with its own `BinaryWriter`; this item's data, once complete, will be stored
        in its `data` attribute, and all items' data can be assembled in order at the end.

        Note the difference compared to packfiles: arrays and strings ALSO get their own items in tagfiles, whereas in
        packfiles, their data just appear after the member field data (which will contain same-item offsets to the
        packed array/string data).
        """
        if (
            debug.DEBUG_PRINT_PACK
            and not debug.DO_NOT_DEBUG_PRINT_PRIMITIVES
            and cls.__name__ not in {"_float", "hkUint8"}
        ):
            tag_data_type_name = cls.get_tag_data_type().name
            debug.debug_print(f"Packing {CYAN}`{cls.__name__}` = {repr(value)}{RESET} <{tag_data_type_name}>")

        if cls.__name__ == "hkRootLevelContainerNamedVariant":
            return tagfile.pack_named_variant(cls, item, value, items, existing_items, item_creation_queues)

        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot pack opaque type (and the file expects no data).
            pass
        elif tag_data_type == TagDataType.Bool:
            tagfile.pack_bool(cls, item, value)
        elif tag_data_type in {TagDataType.CharArray, TagDataType.ConstCharArray}:
            tagfile.pack_string(cls, item, value, items, item_creation_queues)
        elif tag_data_type == TagDataType.Int:
            tagfile.pack_int(cls, item, value)
        elif tag_data_type == TagDataType.Float:
            tagfile.pack_float(cls, item, value)
        elif tag_data_type == TagDataType.Class:
            tagfile.pack_class(cls, item, value, items, existing_items, item_creation_queues)
        elif tag_data_type == TagDataType.Array and cls.__name__ in {"hkPropertyBag", "hkReflectAny"}:
            # TODO: These two newer types are marked as Arrays, for some reason.
            #  Probably indicates that 'Array' actually means some kind of 'Pointer'?
            tagfile.pack_class(cls, item, value, items, existing_items, item_creation_queues)
        else:
            # 'Pointer' and 'Array' types are handled by `Ptr_` and `hkArray_` subclasses, respectively.
            raise ValueError(f"Cannot pack `hk` subclass `{cls.__name__}` with tag data type {tag_data_type.name}.")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileDataItem,
        value: tp.Any,
        existing_items: dict[hk, PackFileDataItem],
        data_pack_queues: PackItemCreationQueues,
    ):
        """Use this `hk` type to process and pack the Python `value`.

        Primitive types and structs can be packed immediately, without creating a new item (whichever item the `writer`
        is currently in is correct). For types with members (Class types), any pointer, array, and string member types
        will cause a new item to be created with its own `BinaryWriter`; this item's data, once complete, will be stored
        in its `raw_data` attribute, and all items' data can be appended in order at the end, followed by their internal
        (child) and external reference pointers.
        """
        if cls.__name__ == "hkRootLevelContainerNamedVariant":
            return packfile.pack_named_variant(cls, item, value, existing_items, data_pack_queues)

        tag_data_type = cls.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot pack opaque type (and the file expects no data).
            pass
        elif tag_data_type == TagDataType.Bool:
            packfile.pack_bool(cls, item, value)
        elif tag_data_type in {TagDataType.CharArray, TagDataType.ConstCharArray}:
            packfile.pack_string(item, value, data_pack_queues)  # `cls` not needed
        elif tag_data_type == TagDataType.Int:
            packfile.pack_int(cls, item, value)
        elif tag_data_type == TagDataType.Float:
            packfile.pack_float(cls, item, value)
        elif tag_data_type == TagDataType.Class:
            packfile.pack_class(cls, item, value, existing_items, data_pack_queues)
        else:
            # 'Pointer' and 'Array' types are handled by `Ptr_` and `hkArray_` subclasses, respectively.
            raise ValueError(f"Cannot pack `hk` subclass `{cls.__name__}` with tag data type {tag_data_type.name}.")

    @classmethod
    def unpack_primitive_array(cls, reader: BinaryReader, length: int, offset: int = None) -> list | np.ndarray | None:
        """Try to unpack an array of this data type more efficiently than the default recursion.

        Unpacks simple arrays of primitive types (invalid/bool/int/float) with a single unpack, e.g. rather than
        unpacking 10000 floats with 10000 sub-calls. Easier to just check subclass tag data type here rather than adding
        an override to every single primitive subclass.

        Overridden by classes with more complicated (but primitive) array formats, e.g. NumPy arrays of vector rows.
        """
        match cls.get_tag_data_type():
            case TagDataType.Invalid:
                # Cannot unpack opaque type (and there shouldn't be anything to unpack in the file).
                return [None] * length
            case TagDataType.Bool:
                fmt = TagDataType.get_int_fmt(cls.tag_type_flags, count=length)
                return [v > 0 for v in reader.unpack(fmt, offset=offset)]
            case TagDataType.Int:
                fmt = TagDataType.get_int_fmt(cls.tag_type_flags, count=length)
                return list(reader.unpack(fmt, offset=offset))

        if cls.tag_type_flags == TagDataType.FloatAndFloat32:
            return list(reader.unpack(f"{length}f", offset=offset))

        return None  # not a primitive array

    @classmethod
    def try_pack_primitive_array(cls, writer: BinaryWriter, value: list | np.ndarray) -> bool:
        """Try to pack an array of primitive types in one call.

        For convenience, checks `cls` name against some basic maths types like `hkVector4` that are technically version-
        specific but still ultimately just a sequence of ints/floats to pack.

        We make no assumptions about how the user has chosen to shape their array. For example, a 2D array could
        represent a `hkStruct[hkVector4f, 4]`, a `hkArray[hkVector4f]`, or a `hkStruct[float, 16]` (flat Havok matrix).
        Every primitive in `value` ultimately needs to be serialized.

        However, the one thing we do NOT support is flat Havok types like `hkStruct[float, 16]` being represented as
        nested lists (e.g. `[[1, 2, 3, 4], [5, 6, 7, 8], ...]`) rather than a (4, 4) NumPy array.

        NOTE: We don't need to validate the length of `value` for fixed-length struct types, as the caller will have
        already done this. The caller has probably already flattened any NumPy array as well.
        """

        if isinstance(value, np.ndarray) and value.ndim > 1:
            # All arrays must be flattened. See docstring.
            value = value.flatten()

        if cls.get_type_name() in {"hkVector4", "hkVector4f"}:
            if isinstance(value, (list, tuple)):
                # Sequence of 4-float vectors/iterables is permitted. We handle it by converting it to a NumPy array,
                # then flattening it, which validates dimensionality at the same time.
                value = np.array(value, dtype=np.float32).flatten()
            writer.pack(f"{len(value)}f", *value)
            return True

        # `value` must be a flat sequence of bools/ints/floats at this point.

        match cls.get_tag_data_type():
            case TagDataType.Invalid:
                return True  # nothing to pack
            case TagDataType.Bool:
                fmt = TagDataType.get_int_fmt(cls.tag_type_flags, count=len(value))
                writer.pack(fmt, *[int(v) for v in value])
                return True
            case TagDataType.Int:
                fmt = TagDataType.get_int_fmt(cls.tag_type_flags, count=len(value))
                writer.pack(fmt, *value)
                return True
            case TagDataType.Float if cls.tag_type_flags == TagDataType.FloatAndFloat32:
                writer.pack(f"{len(value)}f", *value)
                return True

        return False

    @classmethod
    def get_type_info(cls, long_varints: bool) -> TypeInfo:
        """Construct a `TypeInfo` with all information except references to other `TypeInfo`s, which is done later."""
        type_info = TypeInfo(cls.get_real_name())
        type_info.py_class = cls
        if (parent_type_name := cls.__base__.__name__) not in {"hk", "hkBasePointer"}:
            type_info.parent_type_py_name = parent_type_name
        type_info.tag_format_flags = cls.get_tag_format_flags()
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.get_byte_size(long_varints)
        type_info.alignment = cls.get_alignment(long_varints)
        type_info.version = cls.get_version()
        type_info.abstract_value = cls.get_abstract_value()
        type_info.hsh = cls.get_hsh()

        type_info.templates = []
        for template in cls.get_templates():
            if isinstance(template, TemplateValue):
                type_info.templates.append(TemplateInfo(template.name, value=template.value))
            else:
                type_info.templates.append(TemplateInfo(template.name, type_py_name=template.get_type().__name__))

        type_info.members = [
            MemberInfo(
                member.name,
                MemberFlags.Default | member.extra_flags,
                member.offset,
                type_py_name=member.type.__name__,
            )
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
        if member_name[0].isdigit():
            member_name = f"_{member_name}"
        return getattr(self, member_name)

    @classmethod
    def get_real_name(cls) -> str:
        return getattr(cls, f"_{cls.get_type_name(True)}__real_name", cls.__name__)

    @classmethod
    def set_real_name(cls, real_name: str):
        setattr(cls, f"_{cls.get_type_name(True)}__real_name", real_name)

    @classmethod
    def get_tag_format_flags(cls) -> None | int:
        return getattr(cls, f"_{cls.get_type_name(True)}__tag_format_flags", None)

    @classmethod
    def set_tag_format_flags(cls, tag_format_flags: int):
        setattr(cls, f"_{cls.get_type_name(True)}__tag_format_flags", tag_format_flags)

    @classmethod
    def get_hsh(cls) -> None | int:
        return getattr(cls, f"_{cls.get_type_name(True)}__hsh", None)

    @classmethod
    def set_hsh(cls, hsh: int):
        setattr(cls, f"_{cls.get_type_name(True)}__hsh", hsh)

    @classmethod
    def get_abstract_value(cls) -> None | int:
        return getattr(cls, f"_{cls.get_type_name(True)}__abstract_value", None)

    @classmethod
    def set_abstract_value(cls, abstract_value: int):
        setattr(cls, f"_{cls.get_type_name(True)}__abstract_value", abstract_value)

    @classmethod
    def get_version(cls) -> None | int:
        return getattr(cls, f"_{cls.get_type_name(True)}__version", None)

    @classmethod
    def set_version(cls, version: int):
        setattr(cls, f"_{cls.get_type_name(True)}__version", version)

    @classmethod
    def get_templates(cls) -> list[TemplateType | TemplateValue]:
        return getattr(cls, f"_{cls.get_type_name(True)}__templates", [])

    @classmethod
    def set_templates(cls, templates: list[TemplateType | TemplateValue]):
        setattr(cls, f"_{cls.get_type_name(True)}__templates", templates)

    @classmethod
    def get_interfaces(cls) -> list[Interface]:
        return getattr(cls, f"_{cls.get_type_name(True)}__interfaces", [])

    @classmethod
    def set_interfaces(cls, interfaces: list[Interface]):
        setattr(cls, f"_{cls.get_type_name(True)}__interfaces", interfaces)

    @classmethod
    def get_member(cls, member_name: str) -> Member:
        for member in cls.members:
            if member.name == member_name:
                return member
        raise KeyError(f"No member named '{member_name}' in class `{cls.__name__}`.")

    def get_tree_string(
        self,
        indent=0,
        instances_shown: list[hk] = None,
        instances_repeated: set[int] = None,
        max_primitive_sequence_size=-1,
        ignore_basic_defaults=True,
        _is_base_call=True,
    ) -> str:
        """Recursively build indented string of this instance and everything within its members."""
        from .base import hkViewPtr_

        # Set instance tracking lists if this is a base call.
        if instances_shown is None:
            instances_shown = []
        if instances_repeated is None:
            instances_repeated = set()

        lines = [f"{self.__class__.__name__}("]
        for member in self.members:
            member_value = getattr(self, member.py_name)
            if (
                ignore_basic_defaults
                and member.name in ("memSizeAndFlags", "refCount", "memSizeAndRefCount")
                and member_value == 0
            ):
                continue  # skip basic member lines that are default

            if member_value is None or isinstance(member_value, (bool, int, float, str)):
                lines.append(f"    {member.name} = {repr(member_value)},")
            elif isinstance(member_value, np.ndarray):
                if 0 < max_primitive_sequence_size < max(member_value.shape):
                    lines.append(f"    {member.name} = <{member_value.shape}-array>,")
                else:
                    array_str = repr(member_value)
                    array_lines = array_str.split("\n")
                    array_lines[0] = array_lines[0].removeprefix("array(")
                    array_str = f"\n{' ' * (indent + 2)}".join(array_lines)  # lines already indented 6 by Numpy
                    lines.append(f"    {member.name} = array(\n{' ' * (indent + 8)}{array_str},")
            elif issubclass(member.type, hkViewPtr_):
                # Reference is likely to be circular: a value that has not even finished being written yet (and we
                # don't know what the instance number will be yet).
                lines.append(
                    f"    {member.name} = {member_value.__class__.__name__}(),"
                    f"  # <VIEW>"
                )
            elif isinstance(member_value, hk):
                if member_value in instances_shown:
                    lines.append(
                        f"    {member.name} = {member_value.__class__.__name__}(),"
                        f"  # <{instances_shown.index(member_value)}>")
                    instances_repeated.add(id(member_value))
                else:
                    member_str = member_value.get_tree_string(
                        indent + 4, instances_shown, instances_repeated, max_primitive_sequence_size,
                        _is_base_call=False,
                    )
                    lines.append(
                        f"    {member.name} = {member_str},"
                        f"  # <{len(instances_shown)}>"
                    )
                    instances_shown.append(member_value)
            elif isinstance(member_value, list):
                if not member_value:
                    lines.append(f"    {member.name} = [],")
                elif isinstance(member_value[0], hk):
                    lines.append(f"    {member.name} = [")
                    for element in member_value:
                        element: hk
                        if element in instances_shown:
                            lines.append(f"        {element.__class__.__name__},  # <{instances_shown.index(element)}>")
                            instances_repeated.add(id(element))
                        else:
                            element_string = element.get_tree_string(
                                indent + 8, instances_shown, instances_repeated, max_primitive_sequence_size,
                                _is_base_call=False
                            )
                            lines.append(
                                f"        {element_string},  # <{len(instances_shown)}>"
                            )
                            instances_shown.append(element)
                    lines.append(f"    ],")
                elif isinstance(member_value[0], (list, tuple, Quaternion, Vector4)):
                    if 0 < max_primitive_sequence_size < len(member_value):
                        lines.append(
                            f"    {member.name} = [<{len(member_value)} {type(member_value[0]).__name__}>],"
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
                        element: hk
                        if element in instances_shown:
                            lines.append(f"        {element.__class__.__name__},  # <{instances_shown.index(element)}>")
                            instances_repeated.add(id(element))
                        else:
                            element_string = element.get_tree_string(
                                indent + 8, instances_shown, instances_repeated, max_primitive_sequence_size,
                                _is_base_call=False,
                            )
                            lines.append(
                                f"        {element_string},  # <{len(instances_shown)}>"
                            )
                            instances_shown.append(element)
                    lines.append(f"    ),")
                elif isinstance(member_value[0], (list, tuple, Quaternion, Vector4)):
                    if 0 < max_primitive_sequence_size < len(member_value):
                        lines.append(
                            f"    {member.name} = (<{len(member_value)} {type(member_value[0]).__name__}>),"
                        )
                    else:
                        lines.append(f"    {member.name} = (")
                        for element in member_value:
                            lines.append(f"        {repr(element)},")
                        lines.append(f"    ),")
                else:
                    lines.append(f"    {member.name} = {repr(member_value)},")
            elif isinstance(member_value, np.ndarray):
                if 0 < max_primitive_sequence_size < member_value.size:
                    lines.append(
                        f"    {member.name} = <{member_value.shape}-array>,"
                    )
                else:
                    lines.append(f"    {member.name} = {repr(member_value)},")
            elif isinstance(member_value, (Quaternion, Vector4)):
                lines.append(f"    {member.name} = {repr(member_value)},")
            else:
                raise TypeError(f"Cannot parse value of member '{member.name}' for tree string: {type(member_value)}")
        lines.append(")")
        tree_str = f"\n{' ' * indent}".join(lines)
        if _is_base_call:
            repeated_count = 0
            for i, instance in enumerate(instances_shown):
                if id(instance) in instances_repeated:
                    tree_str = tree_str.replace(f",  # <{i}>\n", f",  # <{repeated_count}>\n")
                    repeated_count += 1
                else:  # instance never repeated; strip out index comments
                    tree_str = tree_str.replace(f",  # <{i}>\n", ",\n")
        return tree_str

    def __eq__(self, other: hk):
        """Compares by object ID."""
        return self is other
    
    def __hash__(self):
        """Hashes by object ID."""
        return id(self)

    def __repr__(self):
        return f"{type(self).__name__}()"

    def get_full_repr(self, indent=0):
        ind = " " * indent
        lines = [f"{ind}{type(self).__name__}("]
        for member in self.members:
            lines.append(f"{ind}    {member.name} = {repr(getattr(self, member.py_name))},")
        lines.append(f"{ind})")
        return "\n".join(lines)


HK_TYPE = type[hk]
