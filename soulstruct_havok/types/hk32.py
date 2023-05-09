"""Wrapped import of `types.hk` that includes 32-bit generic type factory functions."""
from __future__ import annotations

__all__ = [
    # hk
    "hk",
    "HK_TYPE",
    "TemplateType",
    "TemplateValue",
    "Member",
    "Interface",
    "DefType",

    # base
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

    # 32-bit factory functions
    "Ptr",
    "hkRefPtr",
    "hkRefVariant",
    "hkArray",
    "hkViewPtr",
    "hkRelArray",
    "hkEnum",
    "hkStruct",
    "hkGenericStruct",
    "hkFreeListArrayElement",
    "hkFreeListArray",
    "hkFlags",
]
import typing as tp


from soulstruct_havok.enums import TagDataType, MemberFlags
from .hk import *
from .base import *


def Ptr(data_type: HK_TYPE | DefType, hsh: int = None) -> tp.Type[Ptr_]:
    """Create a `_Ptr` subclass dynamically, pointing to a particular type."""
    data_type_name = data_type.type_name if isinstance(data_type, DefType) else data_type.__name__
    # noinspection PyTypeChecker
    ptr_type = type(f"Ptr[{data_type_name}]", (Ptr_,), {})  # type: tp.Type[Ptr_]
    ptr_type.set_data_type(data_type)
    ptr_type.alignment = 4
    ptr_type.byte_size = 4
    ptr_type.set_hsh(hsh)
    return ptr_type


def hkRefPtr(data_type: HK_TYPE | DefType, hsh: int = None) -> tp.Type[hkRefPtr_]:
    """Create a `_hkRefPtr` subclass dynamically, pointing to a particular type."""
    data_type_name = data_type.type_name if isinstance(data_type, DefType) else data_type.__name__
    # noinspection PyTypeChecker
    ptr_type = type(f"hkRefPtr[{data_type_name}]", (hkRefPtr_,), {})  # type: tp.Type[hkRefPtr_]
    ptr_type.set_data_type(data_type)
    ptr_type.alignment = 4
    ptr_type.byte_size = 4
    ptr_type.set_hsh(hsh)
    return ptr_type


def hkRefVariant(data_type: HK_TYPE | DefType, hsh: int = None) -> tp.Type[hkRefVariant_]:
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
    ptr_type.set_data_type(data_type)
    ptr_type.alignment = 4
    ptr_type.byte_size = 4
    ptr_type.set_hsh(hsh)
    return ptr_type


def hkArray(data_type: HK_TYPE | hkRefPtr_ | hkViewPtr_, hsh: int = None) -> tp.Type[hkArray_]:
    """Generates an array class with given `data_type` and (optionally) hash."""
    # noinspection PyTypeChecker
    array_type = type(f"hkArray[{data_type.__name__}]", (hkArray_,), {})  # type: tp.Type[hkArray_]
    array_type.set_data_type(data_type)
    array_type.set_hsh(hsh)
    return array_type


def hkViewPtr(data_type_name: str, hsh: int = None) -> tp.Type[hkViewPtr_]:
    """Create a `_hkViewPtr` subclass dynamically.

    To avoid Python circular imports, it is necessary to retrieve the type dynamically here from the module set in `hk`.
    """
    # noinspection PyTypeChecker
    ptr_type = type(f"hkViewPtr[{data_type_name}]", (hkViewPtr_,), {})  # type: tp.Type[hkViewPtr_]
    ptr_type.set_data_type(DefType(data_type_name, lambda: hk.get_module_type(data_type_name)))
    ptr_type.alignment = 4
    ptr_type.byte_size = 4
    ptr_type.set_hsh(hsh)
    return ptr_type


def hkRelArray(data_type: HK_TYPE) -> tp.Type[hkRelArray_]:
    """Create a `hkRelArray_` subclass dynamically."""
    data_type_name = data_type.type_name if isinstance(data_type, DefType) else data_type.__name__
    # noinspection PyTypeChecker
    rel_array_type = type(f"hkRelArray[{data_type_name}]", (hkRelArray_,), {})  # type: tp.Type[hkRelArray_]
    rel_array_type.set_data_type(data_type)
    return rel_array_type


def hkEnum(enum_type: HK_TYPE, storage_type: HK_TYPE) -> tp.Type[hkEnum_]:
    """Generates a `_hkEnum` subclass dynamically."""
    # noinspection PyTypeChecker
    wrapper_type = type(f"hkEnum[{enum_type.__name__}]", (hkEnum_,), {})  # type: tp.Type[hkEnum_]
    wrapper_type.enum_type = enum_type
    wrapper_type.storage_type = storage_type
    return wrapper_type


def hkStruct(data_type: HK_TYPE, length: int) -> tp.Type[hkStruct_]:
    """Generates a `hkStruct_` subclass dynamically.

    Needs all the basic `hk` information, unfortunately, as it can vary (except `tag_format_flags`, which is always 11).
    """
    # noinspection PyTypeChecker
    struct_type = type(f"hkStruct[{data_type.__name__}, {length}]", (hkStruct_,), {})  # type: tp.Type[hkStruct_]
    struct_type.is_generic = False
    struct_type.set_data_type(data_type)
    if length > 255:
        raise ValueError(f"Maximum `hkStruct` (`T[N]`) length is 255. Invalid: {length}")
    struct_type.length = length
    struct_type.tag_type_flags = TagDataType.Struct | length << 8
    return struct_type


def hkGenericStruct(data_type: HK_TYPE, length: int) -> tp.Type[hkStruct_]:
    """Generates a `hkStruct_` subclass dynamically.

    Needs all the basic `hk` information, unfortunately, as it can vary (except `tag_format_flags`, which is always 11).
    """
    # noinspection PyTypeChecker
    struct_type = type(f"hkStruct[{data_type.__name__}, {length}]", (hkStruct_,), {})  # type: tp.Type[hkStruct_]
    struct_type.is_generic = True
    struct_type.set_data_type(data_type)
    if length > 255:
        raise ValueError(f"Maximum `hkStruct` (`T[N]`) length is 255. Invalid: {length}")
    struct_type.length = length
    struct_type.tag_type_flags = TagDataType.Struct | length << 8
    return struct_type


def hkFreeListArrayElement(parent_type: HK_TYPE):
    """NOTE: This super-shallow subclass is not represented anywhere else."""
    # noinspection PyTypeChecker
    element_type = type(f"hkFreeListArrayElement[{parent_type.__name__}]", (parent_type,), {})  # type: HK_TYPE
    element_type.set_tag_format_flags(0)  # shallow subclass
    return element_type  # nothing else to change


def hkFreeListArray(
    elements_data_type: HK_TYPE,
    first_free_data_type: HK_TYPE,
    elements_hsh: int = None,
) -> tp.Type[hkFreeListArray_]:
    if isinstance(elements_data_type, DefType):
        elements_data_type_name = elements_data_type.type_name
    else:
        elements_data_type_name = elements_data_type.__name__
    first_free_data_type_name = first_free_data_type.__name__  # e.g., `hkInt32`
    # noinspection PyTypeChecker
    hk_free_list_array_type = type(
        f"hkFreeListArray[{elements_data_type_name}, {first_free_data_type_name}]",
        (hkFreeListArray_,),
        {},
    )  # type: tp.Type[hkFreeListArray_]
    hk_free_list_array_type.local_members = (
        Member(0, "elements", hkArray(elements_data_type, hsh=elements_hsh), MemberFlags.Protected),
        Member(16, "firstFree", first_free_data_type, MemberFlags.Protected),
    )
    hk_free_list_array_type.members = hk_free_list_array_type.local_members
    return hk_free_list_array_type


def hkFlags(storage_type: HK_TYPE, hsh: int = None) -> tp.Type[hkFlags_]:
    # noinspection PyTypeChecker
    flags_type = type(f"hkFlags[{storage_type.__name__}]", (hkFlags_,), {})  # type: tp.Type[hkFlags_]
    flags_type.alignment = storage_type.alignment
    flags_type.byte_size = storage_type.byte_size
    flags_type.tag_type_flags = storage_type.tag_type_flags
    flags_type.set_hsh(hsh)
    flags_type.local_members = (
        Member(0, "storage", storage_type, MemberFlags.Protected),
    )
    flags_type.members = flags_type.local_members
    return flags_type
