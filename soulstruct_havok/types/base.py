from __future__ import annotations

__all__ = [
    "hkBasePointer",
    "hkContainerHeapAllocator",
    "Ptr_",
    "hkReflectQualifiedType_",
    "hkRefPtr_",
    "hkRefVariant_",
    "hkViewPtr_",
    "hkRelArray_",
    "hkArray_",
    "hkEnum_",
    "hkStruct_",
    "hkFreeListArray_",
    "hkFlags_",
]

import typing as tp

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.tagfile.structs import TagFileItem
from soulstruct_havok.types.info import *

from .hk import hk, DefType
from . import tagfile, packfile, debug

if tp.TYPE_CHECKING:
    from collections import deque
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.packfile.structs import PackFileItem


class hkBasePointer(hk):
    """Intermediate base type shared by types with a `_data_type` attribute and `get_data_type()` method."""
    _data_type = None  # type: tp.Type[hk] | DefType

    @classmethod
    def get_data_type(cls):
        if isinstance(cls._data_type, DefType):
            # First-time data type retrieval; resolve action into data type.
            cls._data_type = cls._data_type.action()
            return cls._data_type
        return cls._data_type

    @classmethod
    def set_data_type(cls, data_type: tp.Type[hk] | DefType):
        cls._data_type = data_type

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


class hkContainerHeapAllocator(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = 7

    __tag_format_flags = 57
    __abstract_value = 16
    local_members = ()


class Ptr_(hkBasePointer):
    """Wrapper for a 'T*' generic pointer, which always points to a fixed type.

    This is necessary because some members, of 'Class' type, use data that is locally stored inside the same item,
    whereas others use these pointers and store their data in different items.

    Differs from `hkRefPtr` below, which has a 'ptr' member of this type and a `tTYPE` template of the pointer's data
    type.
    """
    alignment = 8  # will be 4 for 32-bit-offset files (e.g. PTDE)
    byte_size = 8  # will be 4 for 32-bit-offset files (e.g. PTDE)
    tag_type_flags = 6

    __tag_format_flags = 11

    @classmethod
    def unpack_tagfile(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> hk:
        """Just a pointer."""
        reader.seek(offset)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... ({cls.get_tag_data_type().name})")
        value = tagfile.unpack_pointer(cls.get_data_type(), reader, items)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"-> {value}")
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItem, offset: int = None):
        offset = entry.reader.seek(offset) if offset is not None else entry.reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... (-> {cls.get_tag_data_type().name}) <{hex(offset)}>")
        value = packfile.unpack_pointer(cls.get_data_type(), entry)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"-> {value}")
        # entry.reader.seek(offset + cls.byte_size)  # TODO: unnecessary and byte size is wrong for 32-bit
        return value

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: hk,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing `{cls.__name__}`...")
        tagfile.pack_pointer(cls, item, value, items, existing_items, item_creation_queue)
        if debug.REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItem,
        value: hk,
        existing_items: dict[hk, PackFileItem],
        data_pack_queue: dict[str, deque[tp.Callable]],
    ):
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing `{cls.__name__}`...")
        packfile.pack_pointer(cls, item, value, existing_items, data_pack_queue)
        if debug.REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        pointer_type_py_name = cls.get_data_type().__name__
        type_info = TypeInfo("T*")

        type_info.templates = [TemplateInfo("tT", type_py_name=pointer_type_py_name)]
        type_info.pointer_type_py_name = pointer_type_py_name
        type_info.tag_format_flags = cls.get_tag_format_flags()
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.byte_size
        type_info.alignment = cls.alignment
        type_info.hsh = cls.get_hsh()
        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-4])  # exclude this, `hkBasePointer`, `hk`, and `object`

    @classmethod
    def get_default_value(cls):
        return None


class hkReflectQualifiedType_(Ptr_):
    """Simple wrapper for a special pointer type that has a `tTYPE` template with type `hkReflectType` and a `type`
    member that always points to `hkReflectType`.

    This pointer never actually varies, and presumably just indicates some reflective member that doesn't matter for
    our purposes here.
    """
    alignment = 8  # will be 4 for 32-bit-offset files (e.g. PTDE)
    byte_size = 8  # will be 4 for 32-bit-offset files (e.g. PTDE)
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
        type_info.tag_format_flags = cls.get_tag_format_flags()
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.byte_size
        type_info.alignment = cls.alignment
        type_info.hsh = cls.get_hsh()
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
    alignment = 8  # will be set to 4 if appropriate (for `long_varints=False`)
    byte_size = 8  # will be set to 4 if appropriate (for `long_varints=False`)
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
        type_info.tag_format_flags = cls.get_tag_format_flags()
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.byte_size
        type_info.alignment = cls.alignment
        type_info.hsh = cls.get_hsh()
        type_info.pointer_type_py_name = cls.get_data_type().__name__
        type_info.members = [
            MemberInfo("ptr", flags=36, offset=0, type_py_name=f"Ptr[{cls.get_data_type().__name__}]"),
        ]

        return type_info


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

        type_info.tag_format_flags = cls.get_tag_format_flags()
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.byte_size
        type_info.alignment = cls.alignment
        type_info.hsh = cls.get_hsh()
        type_info.pointer_type_py_name = cls.get_data_type().__name__
        type_info.members = [
            MemberInfo("ptr", flags=36, offset=0, type_py_name=f"Ptr[{cls.get_data_type().__name__}]"),
        ]

        return type_info


class hkViewPtr_(hkBasePointer):
    """Pointer that is used as a recursive reference to a containing owner instance.

    Like `DefType`, this is defined in Python using a type name string and action to avoid circular imports, but unlike
    `DefType` (which is just a `Ptr` self-reference), this is a real Havok type with its own genuine type data, and the
    use of `DefType` is internal rather than declared in the member.
    """
    alignment = 8  # will be set to 4 if appropriate (for `long_varints=False`)
    byte_size = 8  # will be set to 4 if appropriate (for `long_varints=False`)
    tag_type_flags = 6

    __tag_format_flags = 59
    __abstract_value = 64

    @classmethod
    def unpack_tagfile(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> hk:
        """Identical to `Ptr`."""
        reader.seek(offset)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... ({cls.get_tag_data_type().name})")
        value = tagfile.unpack_pointer(cls.get_data_type(), reader, items)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"-> {value}")
        return value

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: hk,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        """Identical to `Ptr`.

        TODO: This might queue up item creation at hkViewPtr time rather than when the actual parent item finishes.
         May cause issues or at least break my otherwise byte-perfect item order.
        """
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing `{cls.__name__}`...")
        tagfile.pack_pointer(cls, item, value, items, existing_items, item_creation_queue)
        if debug.REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        data_type_name = cls.get_data_type().__name__
        type_info = TypeInfo("hkViewPtr")
        type_info.py_class = cls

        type_info.templates = [
            TemplateInfo("tTYPE", type_py_name=data_type_name),
        ]
        type_info.tag_format_flags = cls.get_tag_format_flags()
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.byte_size
        type_info.alignment = cls.alignment
        type_info.abstract_value = cls.get_abstract_value()
        type_info.pointer_type_py_name = data_type_name
        # `hkViewPtr` hash is actually its pointer's hash; `hkViewPtr` has no hash.
        type_info.members = [
            MemberInfo("ptr", flags=36, offset=0, type_py_name=f"Ptr[{data_type_name}]"),
        ]

        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-4])  # exclude this, `hkBasePointer`, `hk`, and `object`

    @classmethod
    def get_default_value(cls):
        return None


class hkRelArray_(hkBasePointer):
    """Wrapper for a rare type of pointer that only appears in some `hknp` classes.

    It reads `length` and `jump` shorts, and uses that offset to make a jump ahead (from just before `length`) to
    a tightly packed array of some data type, which is unpacked into a list like regular `hkArray` types.
    """
    byte_size = 4
    alignment = 2
    tag_type_flags = 6

    __tag_format_flags = 43

    @classmethod
    def unpack_tagfile(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> list:
        offset = reader.seek(offset) if offset is not None else reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... ({cls.get_data_type().__name__}) <{hex(offset)}>")

        source_offset = reader.position
        length, jump = reader.unpack("<HH")
        with reader.temp_offset(source_offset + jump):
            if debug.DEBUG_PRINT_UNPACK:
                debug.increment_debug_indent()
            array_start_offset = reader.position
            value = [
                cls.get_data_type().unpack_tagfile(
                    reader,
                    offset=array_start_offset + i * cls.get_data_type().byte_size,
                    items=items,
                ) for i in range(length)
            ]
            if debug.DEBUG_PRINT_UNPACK:
                debug.decrement_debug_indent()
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"-> {value}")
        reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItem, offset: int = None) -> list:
        offset = entry.reader.seek(offset) if offset is not None else entry.reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... ({cls.get_data_type().__name__}) <{hex(offset)}>")

        if debug.DEBUG_PRINT_UNPACK:
            debug.increment_debug_indent()
        source_offset = entry.reader.position
        length, jump = entry.reader.unpack("<HH")
        with entry.reader.temp_offset(source_offset + jump):
            array_start_offset = entry.reader.position
            data_type = cls.get_data_type()
            value = [
                data_type.unpack_packfile(
                    entry,
                    offset=array_start_offset + i * data_type.byte_size,
                ) for i in range(length)
            ]
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"-> {value}")
        entry.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: hk,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        # TODO: This DOES appear in tagfiles that use classes like `hknpConvexShape`.
        #  Examine those classes closely to find out where the relative array is written (and the jump size).
        raise TypeError("Have not encountered `hkRelArray` types in tagfiles before. Cannot pack them.")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItem,
        value: tuple,
        existing_items: dict[hk, PackFileItem],
        data_pack_queue: dict[str, deque[tp.Callable]],
    ):
        """Registers a function that will write the `hkRelArray` contents, and fill its length/jump where appropriate.

        This function will be called when the current list (pushed by last `pack_class_packfile()` call) is popped. That
        is, once class members have all been done.
        """
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing `{cls.__name__}`...")
        rel_array_header_pos = item.writer.position
        item.writer.pack("<HH", len(value), 0)

        if len(value) == 0:
            return

        def delayed_rel_array():
            jump = item.writer.position - rel_array_header_pos
            if debug.DEBUG_PRINT_PACK:
                debug.debug_print(f"Writing `hkRelArray` and writing jump {jump} at offset {rel_array_header_pos}.")
            item.writer.pack_at(rel_array_header_pos, "<HH", len(value), jump)
            data_type = cls.get_data_type()
            array_start_offset = item.writer.position
            for i, element in enumerate(value):
                item.writer.pad_to_offset(array_start_offset + i * data_type.byte_size)
                data_type.pack_packfile(item, element, existing_items, data_pack_queue)

        item.pending_rel_arrays[-1].append(delayed_rel_array)

        if debug.REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        raise TypeError("Cannot convert `hkRelArray_` to `TypeInfo` yet for packing packfiles.")

    @classmethod
    def get_type_hierarchy(cls) -> list[tp.Type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-4])  # exclude this, `hk`, `hkBasePointer`, and `object`

    @classmethod
    def get_default_value(cls):
        return []


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

    _data_type: tp.Type[hk] | hkRefPtr_ | hkViewPtr_ | DefType

    @classmethod
    def unpack_tagfile(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> list:
        reader.seek(offset)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`...")
            debug.increment_debug_indent()
        value = tagfile.unpack_array(cls.get_data_type(), reader, items)
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
            debug.debug_print(f"-> {repr(value)}")
        if debug.REQUIRE_INPUT:
            input("Continue?")
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItem, offset: int = None):
        offset = entry.reader.seek(offset) if offset is not None else entry.reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... <{hex(offset)}>")
            debug.increment_debug_indent()
        value = packfile.unpack_array(cls.get_data_type(), entry)
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
            debug.debug_print(f"-> {repr(value)}")
        if debug.REQUIRE_INPUT:
            input("Continue?")
        entry.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: list[hk] | list[int] | list[float] | list[str] | list[bool],
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        """Remember that array length can be variable, unlike `hkStruct`."""
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing `{cls.__name__}`... (length = {len(value)})")
        tagfile.pack_array(cls, item, value, items, existing_items, item_creation_queue)
        if debug.REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItem,
        value: list[hk] | list[int] | list[float] | list[str] | list[bool],
        existing_items: dict[hk, PackFileItem],
        data_pack_queue: dict[str, deque[tp.Callable]],
    ):
        """Remember that array length can be variable, unlike `hkStruct`."""
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing `{cls.__name__}`... (length = {len(value)}) at {item.writer.position_hex}")
        packfile.pack_array(cls, item, value, existing_items, data_pack_queue)
        if debug.REQUIRE_INPUT:
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
        type_info.hsh = cls.get_hsh()
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

    @classmethod
    def get_default_value(cls):
        return []


class hkEnum_(hk):
    """Base for simple wrapper types (generated with `hkEnum` function below) that combines a storage type with a
    data type (whose sizes may not match). The name of the enum class is given by the data type. The storage type is
    usually `hkUint8`.

    Note that it is actually possible to extract enum value names from packfiles.
    """
    enum_type = None  # type: tp.Type[hk]
    storage_type = None  # type: tp.Type[hk]

    @classmethod
    def unpack_tagfile(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = ()):
        # TODO: Parse using storage type or data type? Storage, I think...
        return cls.storage_type.unpack_tagfile(reader, offset, items)

    @classmethod
    def unpack_packfile(cls, entry: PackFileItem, offset: int = None):
        # TODO: Parse using storage type or data type? Storage, I think...
        return cls.storage_type.unpack_packfile(entry, offset)

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: tp.Any,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        return cls.storage_type.pack_tagfile(item, value, items, existing_items, item_creation_queue)

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItem,
        value: tp.Any,
        existing_items: dict[hk, PackFileItem],
        data_pack_queue: dict[str, deque[tp.Callable]],
    ):
        return cls.storage_type.pack_packfile(item, value, existing_items, data_pack_queue)

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

    @classmethod
    def get_default_value(cls):
        return 0


class hkStruct_(hkBasePointer):
    """Simple wrapper type for both 'T[N]' types and built-in tuple types like `hkVector4f`.

    These types store a fixed amount of data locally (e.g., within the same item) rather than separately, like arrays.

    NOTE: For generic 'T[N]' tuples, length is actually stored twice: in the 'vN' template, and in the second most
    significant byte of `tag_type_flags`. (In non-generic tuples, there is no 'vN' template, just the `tag_type_flags`.)
    """
    length = 0
    is_generic = False

    @classmethod
    def unpack_tagfile(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> tuple:
        reader.seek(offset)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... (Struct) <{hex(offset)}>")
            debug.increment_debug_indent()
        value = tagfile.unpack_struct(cls.get_data_type(), reader, items, cls.length)
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
            debug.debug_print(f"-> {repr(value)}")
        return value

    @classmethod
    def unpack_packfile(cls, entry: PackFileItem, offset: int = None) -> tuple:
        offset = entry.reader.seek(offset) if offset is not None else entry.reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... (Struct) <{hex(offset)}>")
            debug.increment_debug_indent()
        value = packfile.unpack_struct(cls.get_data_type(), entry, length=cls.length)
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
            debug.debug_print(f"-> {repr(value)}")
        entry.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: tp.Any,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queue: dict[str, deque[tp.Callable]],
    ):
        tagfile.pack_struct(cls.get_data_type(), item, value, items, existing_items, item_creation_queue, cls.length)

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileItem,
        value: tp.Any,
        existing_items: dict[hk, PackFileItem],
        data_pack_queue: dict[str, deque[tp.Callable]],
    ):
        packfile.pack_struct(
            cls.get_data_type(), item, value, existing_items, data_pack_queue, cls.length
        )

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        data_type = cls.get_data_type()
        if cls.is_generic:
            data_type_py_name = data_type.__name__
            type_info = TypeInfo("T[N]")
            type_info.py_class = cls
            type_info.pointer_type_py_name = data_type_py_name

            type_info.templates = [
                TemplateInfo("tT", type_py_name=data_type_py_name),
                TemplateInfo("vN", value=cls.length),
            ]
            type_info.tag_format_flags = 11
            type_info.tag_type_flags = cls.tag_type_flags  # already set to correct subtype (including length)
            type_info.byte_size = data_type.byte_size * cls.length
            type_info.alignment = data_type.alignment
            # TODO: Some generic T[N] types have hashes. Could find it here from XML...
        else:
            # Default method is fine, but we may remove the parent class and add a `data_type` pointer.
            type_info = super().get_type_info()

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
            # exclude `hkStruct_[type, length]` subclass, this, `hkBasePointer`, `hk`, and `object`
            # noinspection PyTypeChecker
            return list(cls.__mro__[:-5])

    @classmethod
    def get_default_value(cls):
        return ()


class hkFreeListArray_(hk):
    """Generic name for a class with an 'elements' member that is a `hkArray[hkFreeListArrayElement]` instance.

    Multiple types with this name can be defined, uniquely identified by their 'elements' array data type.
    """
    byte_size = 24
    alignment = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    # `__hsh` is set dynamically.

    # `local_members` (and `members`) defined by class creation function.


class hkFlags_(hk):
    """Generic flags type that is basically a shallow enum-like wrapper around a certain 'storage' int type."""
    # `byte_size`, `alignment`, and `tag_type_flags` are set dynamically from 'storage' type.
    __tag_format_flags = 41
    # `__hsh` is set dynamically (probably never used).

    # `local_members` and `members` (lone 'storage' member) are set dynamically.

    @classmethod
    def get_default_value(cls):
        return 0
