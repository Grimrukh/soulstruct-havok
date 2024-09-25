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
from enum import IntEnum

import colorama
import numpy as np

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.packfile.structs import PackItemCreationQueues, PackFileDataItem
from soulstruct_havok.tagfile.structs import TagItemCreationQueues, TagFileItem
from soulstruct_havok.types.info import *

from .hk import hk, DefType
from . import tagfile, packfile, debug

if tp.TYPE_CHECKING:
    from collections import deque
    from soulstruct.utilities.binary import BinaryReader

colorama.just_fix_windows_console()
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
YELLOW = colorama.Fore.YELLOW
BLUE = colorama.Fore.BLUE
CYAN = colorama.Fore.CYAN
MAGENTA = colorama.Fore.MAGENTA
RESET = colorama.Fore.RESET


class hkBasePointer(hk):
    """Intermediate base type shared by types with a `_data_type` attribute and `get_data_type()` method."""
    _data_type = None  # type: type[hk] | DefType

    @classmethod
    def get_data_type(cls):
        if isinstance(cls._data_type, DefType):
            # First-time data type retrieval; resolve action into data type.
            cls._data_type = cls._data_type.action()
            return cls._data_type
        return cls._data_type

    @classmethod
    def set_data_type(cls, data_type: type[hk] | DefType):
        cls._data_type = data_type

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        """Default implementation for pointer classes."""
        type_info = super().get_type_info()
        type_info.pointer_type_py_name = cls.get_data_type().__name__
        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[type[hk]]:
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
            debug.debug_print(f"Unpacking `{cls.__name__}`... ({cls.get_tag_data_type().name}) <{hex(offset)}>")
        value = tagfile.unpack_pointer(cls.get_data_type(), reader, items)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"-> {value}")
        return value

    @classmethod
    def unpack_packfile(cls, item: PackFileDataItem, offset: int = None):
        offset = item.reader.seek(offset) if offset is not None else item.reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... (-> {cls.get_tag_data_type().name}) <{hex(offset)}>")
        value = packfile.unpack_pointer(cls.get_data_type(), item)
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
        item_creation_queues: TagItemCreationQueues = None,
    ):
        tagfile.pack_pointer(cls, item, value, items, existing_items, item_creation_queues)
        if debug.REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileDataItem,
        value: hk,
        existing_items: dict[hk, PackFileDataItem],
        data_pack_queues: PackItemCreationQueues,
    ):
        packfile.pack_pointer(cls, item, value, existing_items, data_pack_queues)
        if debug.REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        pointer_type_py_name = cls.get_data_type().__name__
        type_info = TypeInfo("T*")

        type_info.templates = [TemplateInfo("tT", type_py_name=pointer_type_py_name)]
        type_info.pointer_type_py_name = pointer_type_py_name
        type_info.tag_format_flags = cls.__tag_format_flags
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.byte_size
        type_info.alignment = cls.alignment
        type_info.hsh = cls.get_hsh()  # pointer type specific (or `None`)
        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[type[hk]]:
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
    def get_type_hierarchy(cls) -> list[type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-5])  # exclude this, `_Ptr`, `hkBasePointer`, `hk`, and `object`

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        type_info = TypeInfo("hkReflect::QualifiedType")
        type_info.py_class = cls

        type_info.templates = [
            TemplateInfo("tTYPE", type_py_name="hkReflectType"),
        ]
        type_info.tag_format_flags = cls.__tag_format_flags
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
    def get_type_hierarchy(cls) -> list[type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-5])  # exclude this, `_Ptr`, `hkBasePointer`, `hk`, and `object`

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        type_info = TypeInfo("hkRefPtr")
        type_info.py_class = cls

        type_info.templates = [
            TemplateInfo("tTYPE", type_py_name=cls.get_data_type().__name__),
        ]
        type_info.tag_format_flags = cls.__tag_format_flags
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
    def get_type_hierarchy(cls) -> list[type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-5])  # exclude this, `Ptr_`, `hkBasePointer`, `hk`, and `object`

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        type_info = TypeInfo("hkRefVariant")
        type_info.py_class = cls

        type_info.tag_format_flags = cls.__tag_format_flags
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
            debug.debug_print(f"Unpacking `{cls.__name__}`... ({cls.get_tag_data_type().name}) <{hex(offset)}>")
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
        item_creation_queues: TagItemCreationQueues = None,
    ):
        """Identical to `Ptr`.

        TODO: This might queue up item creation at hkViewPtr time rather than when the actual parent item finishes.
         May cause issues or at least break my otherwise byte-perfect item order.
        """
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing `{cls.__name__}`...")
        tagfile.pack_pointer(cls, item, value, items, existing_items, item_creation_queues)
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
        type_info.tag_format_flags = cls.__tag_format_flags
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.byte_size
        type_info.alignment = cls.alignment
        type_info.abstract_value = cls.__abstract_value
        type_info.pointer_type_py_name = data_type_name
        # `hkViewPtr` hash is actually its pointer's hash; `hkViewPtr` has no hash.
        type_info.members = [
            MemberInfo("ptr", flags=36, offset=0, type_py_name=f"Ptr[{data_type_name}]"),
        ]

        return type_info

    @classmethod
    def get_type_hierarchy(cls) -> list[type[hk]]:
        # noinspection PyTypeChecker
        return list(cls.__mro__[:-4])  # exclude this, `hkBasePointer`, `hk`, and `object`

    @classmethod
    def get_default_value(cls):
        return None


class hkRelArray_(hkBasePointer):
    """Wrapper for a rare type of pointer that only appears in some `hknp` classes.

    It reads `length` and `jump` shorts, and uses that offset to make a jump ahead (from just before `length`) to
    a tightly packed array of some data type, which is unpacked into a list or NumPy array like regular `hkArray` types.
    """
    byte_size = 4
    alignment = 2
    tag_type_flags = 6

    __tag_format_flags = 43

    @classmethod
    def unpack_tagfile(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> list | np.ndarray:
        offset = reader.seek(offset) if offset is not None else reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... ({cls.get_data_type().__name__}) <{hex(offset)}>")

        source_offset = reader.position
        length, jump = reader.unpack("<HH")
        with reader.temp_offset(source_offset + jump):
            if debug.DEBUG_PRINT_UNPACK:
                debug.increment_debug_indent()
            data_type = cls.get_data_type()
            if data_type.__name__ in {"hkVector3", "hkVector3f"}:
                # Read tight array of vectors.
                data = reader.read(length * 12)
                dtype = np.dtype(f"{reader.default_byte_order}f4")
                value = np.frombuffer(data, dtype=dtype).reshape((length, 3))
            elif data_type.__name__ in {"hkVector4", "hkVector4f"}:
                # Read tight array of vectors.
                data = reader.read(length * 16)
                dtype = np.dtype(f"{reader.default_byte_order}f4")
                value = np.frombuffer(data, dtype=dtype).reshape((length, 4))
            else:  # unpack array as list
                array_start_offset = reader.position
                value = [
                    data_type.unpack_tagfile(
                        reader,
                        offset=array_start_offset + i * data_type.byte_size,
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
    def unpack_packfile(cls, item: PackFileDataItem, offset: int = None) -> list:
        offset = item.reader.seek(offset) if offset is not None else item.reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... ({cls.get_data_type().__name__}) <Entry @ {hex(offset)}>")

        if debug.DEBUG_PRINT_UNPACK:
            debug.increment_debug_indent()
        source_offset = item.reader.position
        length, jump = item.reader.unpack("<HH")
        with item.reader.temp_offset(source_offset + jump):
            data_type = cls.get_data_type()
            if data_type.__name__ in {"hkVector3", "hkVector3f"}:
                # Read tight array of vectors.
                data = item.reader.read(length * 12)
                dtype = np.dtype(f"{item.reader.default_byte_order}f4")
                value = np.frombuffer(data, dtype=dtype).reshape((length, 3))
            elif data_type.__name__ in {"hkVector4", "hkVector4f"}:
                # Read tight array of vectors.
                data = item.reader.read(length * 16)
                dtype = np.dtype(f"{item.reader.default_byte_order}f4")
                value = np.frombuffer(data, dtype=dtype).reshape((length, 4))
            else:  # unpack array as list
                array_start_offset = item.reader.position
                value = [
                    data_type.unpack_packfile(
                        item,
                        offset=array_start_offset + i * data_type.byte_size,
                    ) for i in range(length)
                ]
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"-> {value}")
        item.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: hk,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queues: TagItemCreationQueues = None,
    ):
        # TODO: This DOES appear in tagfiles that use classes like `hknpConvexShape`.
        #  Examine those classes closely to find out where the relative array is written (and the jump size).
        raise NotImplementedError("Cannot yet pack Havok types with `hkRelArray` members to tagfiles.")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileDataItem,
        value: tuple,
        existing_items: dict[hk, PackFileDataItem],
        data_pack_queues: PackItemCreationQueues,
    ):
        """Registers a function that will write the `hkRelArray` contents, and fill its length/jump where appropriate.

        This function will be called when the current list (pushed by last `pack_class_packfile()` call) is popped. That
        is, once class members have all been done.
        """
        rel_array_header_pos = item.writer.position
        item.writer.pack("<HH", len(value), 0)

        if len(value) == 0:
            if debug.DEBUG_PRINT_PACK:
                debug.debug_print(f"Packing {MAGENTA}`{cls.__name__}` = <empty>{RESET}")
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
                data_type.pack_packfile(item, element, existing_items, data_pack_queues)

        item.pending_rel_arrays[-1].append(delayed_rel_array)

        if debug.REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def get_type_info(cls) -> TypeInfo:
        raise TypeError("Cannot convert `hkRelArray_` to `TypeInfo` yet for packing packfiles.")

    @classmethod
    def get_type_hierarchy(cls) -> list[type[hk]]:
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

    class Flags(IntEnum):
        """Bit flags that can be set in the highest two bits of the `capacityAndFlags` member of an `hkArray`.

        99% of arrays enable `DONT_DEALLOCATE_FLAG` only. Suspiciously, those that don't are often in FromSoft's custom
        class extensions, so they may have just neglected to enable it.
        """
        DONT_DEALLOCATE_FLAG = 0x80000000  # extremely common; "the storage is not the array's to delete"
        ALLOCATED_FROM_SPU_FLAG = 0x40000000  # PS3-era SDKs; "array storage allocated as a result of a SPU request"
        LOCKED_FLAG = 0x40000000  # older SDKs; "will never have its dtor called (read in from packfile for instance)"

    alignment = 8  # actually aligned to 16 in tag file data
    byte_size = 16
    tag_type_flags = 8

    __tag_format_flags = 43

    flags: int = Flags.DONT_DEALLOCATE_FLAG
    forced_capacity: int | None = None

    _data_type: type[hk] | hkRefPtr_ | hkViewPtr_ | DefType

    @classmethod
    def unpack_tagfile(
        cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None
    ) -> list:
        reader.seek(offset)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... <{hex(offset)}>")
            debug.increment_debug_indent()
        value = tagfile.unpack_array(cls.get_data_type(), reader, items)
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
            if len(value) > 10 and isinstance(value[0], (int, float)):
                debug.debug_print(f"--> {repr(value[:10])}... ({len(value)} elements)")
            else:
                debug.debug_print(f"--> {repr(value)}")
        if debug.REQUIRE_INPUT:
            input("Continue?")
        return value

    @classmethod
    def unpack_packfile(cls, item: PackFileDataItem, offset: int = None):
        offset = item.reader.seek(offset) if offset is not None else item.reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... <{hex(offset)}>")
            debug.increment_debug_indent()
        value = packfile.unpack_array(cls.get_data_type(), item)
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
            if len(value) > 10 and isinstance(value[0], (int, float)):
                debug.debug_print(f"--> {repr(value[:10])}... ({len(value)} elements)")
            else:
                debug.debug_print(f"--> {repr(value)}")
        if debug.REQUIRE_INPUT:
            input("Continue?")
        item.reader.seek(offset + cls.byte_size)
        return value

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: list[hk] | list[int] | list[float] | list[str] | list[bool],
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queues: TagItemCreationQueues = None,
    ):
        """Remember that array length can be variable, unlike `hkStruct`."""
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing `{cls.__name__}`... (length = {len(value)})")
        tagfile.pack_array(cls, item, value, items, existing_items, item_creation_queues)
        if debug.REQUIRE_INPUT:
            input("Continue?")

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileDataItem,
        value: list[hk] | list[int] | list[float] | list[str] | list[bool],
        existing_items: dict[hk, PackFileDataItem],
        data_pack_queues: PackItemCreationQueues,
    ):
        """Remember that array length can be variable, unlike `hkStruct`."""
        packfile.pack_array(cls, item, value, existing_items, data_pack_queues)
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
        type_info.tag_format_flags = cls.__tag_format_flags
        type_info.tag_type_flags = cls.tag_type_flags
        type_info.byte_size = cls.byte_size
        type_info.alignment = cls.alignment
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
    def get_type_hierarchy(cls) -> list[type[hk]]:
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
    enum_type = None  # type: type[hk]
    storage_type = None  # type: type[hk]

    @classmethod
    def unpack_tagfile(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = ()):
        # TODO: Parse using storage type or data type? Storage, I think...
        return cls.storage_type.unpack_tagfile(reader, offset, items)

    @classmethod
    def unpack_packfile(cls, item: PackFileDataItem, offset: int = None):
        # TODO: Parse using storage type or data type? Storage, I think...
        return cls.storage_type.unpack_packfile(item, offset)

    @classmethod
    def pack_tagfile(
        cls,
        item: TagFileItem,
        value: tp.Any,
        items: list[TagFileItem],
        existing_items: dict[hk, TagFileItem],
        item_creation_queues: TagItemCreationQueues = None,
    ):
        return cls.storage_type.pack_tagfile(item, value, items, existing_items, item_creation_queues)

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileDataItem,
        value: tp.Any,
        existing_items: dict[hk, PackFileDataItem],
        data_pack_queues: PackItemCreationQueues,
    ):
        return cls.storage_type.pack_packfile(item, value, existing_items, data_pack_queues)

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
    def get_type_hierarchy(cls) -> list[type[hk]]:
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
    def unpack_packfile(cls, item: PackFileDataItem, offset: int = None) -> tuple:
        offset = item.reader.seek(offset) if offset is not None else item.reader.position
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking `{cls.__name__}`... (Struct) <Entry @ {hex(offset)}>")
            debug.increment_debug_indent()
        value = packfile.unpack_struct(cls.get_data_type(), item, length=cls.length)
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
            debug.debug_print(f"-> {repr(value)}")
        item.reader.seek(offset + cls.byte_size)
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
        tagfile.pack_struct(cls.get_data_type(), item, value, items, existing_items, item_creation_queues, cls.length)

    @classmethod
    def pack_packfile(
        cls,
        item: PackFileDataItem,
        value: tp.Any,
        existing_items: dict[hk, PackFileDataItem],
        data_pack_queues: PackItemCreationQueues,
    ):
        packfile.pack_struct(
            cls.get_data_type(), item, value, existing_items, data_pack_queues, cls.length
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
    def get_type_hierarchy(cls) -> list[type[hk]]:
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
