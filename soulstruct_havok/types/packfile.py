from __future__ import annotations

__all__ = [
    "unpack_int",
    "pack_int",
    "unpack_bool",
    "pack_bool",
    "unpack_float32",
    "pack_float",
    "unpack_class",
    "pack_class",
    "unpack_pointer",
    "pack_pointer",
    "unpack_array",
    "pack_array",
    "unpack_struct",
    "pack_struct",
    "unpack_string",
    "pack_string",
    "unpack_named_variant",
    "pack_named_variant",
]

import typing as tp
from collections import deque

import numpy as np

from soulstruct.utilities.inspection import get_hex_repr

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.packfile.structs import PackFileItem
from .info import get_py_name

from . import debug

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from .hk import hk
    from .base import hkArray_


def unpack_bool(hk_type: tp.Type[hk], reader: BinaryReader) -> bool:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt) > 0


def pack_bool(hk_type: tp.Type[hk], item: PackFileItem, value: bool):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    item.writer.pack(fmt, int(value))


def unpack_int(hk_type: tp.Type[hk], reader: BinaryReader) -> int:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt)


def pack_int(hk_type: tp.Type[hk], item: PackFileItem, value: int):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags, signed=value < 0)
    item.writer.pack(fmt, value)


def unpack_float32(reader: BinaryReader) -> float | hk:
    """32-bit floats are unpacked directly; others (like half floats) are unpacked as classes (Havok's setup)."""
    return reader.unpack_value("<f")


def pack_float(hk_type: tp.Type[hk], item: PackFileItem, value: float | hk):
    if hk_type.tag_type_flags == TagDataType.FloatAndFloat32:
        item.writer.pack("<f", value)
    else:
        # Will definitely not use or create items.
        pack_class(hk_type, item, value, existing_items={}, data_pack_queue={})


def unpack_class(hk_type: tp.Type[hk], item: PackFileItem, instance=None) -> hk:
    """Existing `instance` created by caller can be passed, which is useful for managing recursion.

    NOTE: This is not used for `hkRootLevelContainerNamedVariant`, which uses a special dynamic unpacker to detect the
    appropriate `hkReferencedObject` subclass it points to with its `hkRefVariant` pointer.
    """
    kwargs = {}

    member_start_offset = item.reader.position
    for member in hk_type.members:
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(
                f"Unpacking member '{member.name}' of type `{member.type.__name__}` at offset {hex(member.offset)} "
                f"(item offset {hex(member_start_offset + member.offset)}):"
            )
        if debug.DEBUG_PRINT_UNPACK:
            debug.increment_debug_indent()
        member_value = member.type.unpack_packfile(
            item,
            offset=member_start_offset + member.offset,
        )
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
        kwargs[member.name] = member_value

    if instance is None:
        # noinspection PyArgumentList
        instance = hk_type(**kwargs)
    else:
        for name, value in kwargs.items():
            setattr(instance, name, value)  # type hint will be given in class definition

    return instance


def pack_class(
    hk_type: tp.Type[hk],
    item: PackFileItem,
    value: hk,
    existing_items: dict[hk, PackFileItem],
    data_pack_queue: dict[str, deque[tp.Callable]],
):
    member_start_offset = item.writer.position

    if "hkBaseObject" in [parent_type.__name__ for parent_type in hk_type.get_type_hierarchy()]:
        # Pointer for the mysterious base object type.
        item.writer.pack("<V", 0)

    if debug.DEBUG_PRINT_UNPACK:
        debug.increment_debug_indent()
    item.pending_rel_arrays.append(deque())
    for member in hk_type.members:
        # Member offsets may not be perfectly packed together, so we always pad up to the proper offset.
        item.writer.pad_to_offset(member_start_offset + member.offset)
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(
                f"Member '{member.name}' (type `{type(value[member.name]).__name__} : {member.type.__name__}`) "
                f"at {item.writer.position_hex}:"
            )
        # TODO: with_flag = member.name != "partitions" ?
        member.type.pack_packfile(item, value[member.name], existing_items, data_pack_queue)
        # TODO: Used to pad to member alignment here, but seems redundant.
    item.writer.pad_to_offset(member_start_offset + hk_type.byte_size)
    if debug.DEBUG_PRINT_UNPACK:
        debug.decrement_debug_indent()

    # `hkRelArray` data is written after all members have been checked/written.
    for pending_rel_array in item.pending_rel_arrays.pop():
        pending_rel_array()


def unpack_pointer(data_hk_type: tp.Type[hk], item: PackFileItem) -> hk | None:
    """`data_hk_type` is used to make sure that the referenced item's `hk_type` is a subclass of it."""
    source_offset = item.reader.position
    zero = item.reader.unpack_value("<V")  # "dummy" pointer
    try:
        pointed_item, item_data_offset = item.item_pointers[source_offset]
    except KeyError:
        if zero != 0:
            print(zero, item.item_pointers)
            raise ValueError(
                f"Could not find item pointer: type {item.hk_type.__name__}, buffer at {hex(source_offset)}."
            )
        else:
            return None
    if zero != 0:
        raise AssertionError(f"Found non-zero data at item pointer offset: {zero}.")
    if item_data_offset != 0:
        print(pointed_item.item_pointers)
        raise AssertionError(f"Data item pointer (global ref dest) was not zero: {item_data_offset}.")
    if not issubclass(pointed_item.hk_type, data_hk_type):
        raise ValueError(
            f"Pointer-referenced item type {pointed_item.hk_type.__name__} is not a child of expected type "
            f"{data_hk_type.__name__}."
        )
    if pointed_item.value is None:
        # Unpack item (first time).
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Unpacking NEW ITEM: {pointed_item.hk_type.__name__}")
        pointed_item.start_reader()
        if debug.DEBUG_PRINT_UNPACK:
            debug.increment_debug_indent()
        # NOTE: `pointed_item.hk_type` may be a subclass of `data_hk_type`, so it's important we use it here.
        pointed_item.value = pointed_item.hk_type.unpack_packfile(pointed_item)
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
    else:
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Existing pointed item: {type(pointed_item.value).__name__}")
    return pointed_item.value


def pack_pointer(
    data_hk_type: tp.Type[hk],
    item: PackFileItem,
    value: hk,
    existing_items: dict[hk, PackFileItem],
    data_pack_queue: dict[str, deque[tp.Callable]],
):
    """Pointer to another item, which may or may not have already been created."""
    if value is None:
        # Null pointer. Space is left for a global fixup, but it will never have a fixup.
        item.writer.pack("<V", 0)  # global item fixup
        return

    if value in existing_items:
        item.item_pointers[item.writer.position] = (existing_items[value], 0)
        item.writer.pack("<V", 0)  # global item fixup
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Existing item: {type(existing_items[value]).__name__}")
        return
    else:
        # NOTE: This uses the data type, NOT the `Ptr` type. Copies `long_varints` from source item.
        new_item = existing_items[value] = PackFileItem(hk_type=data_hk_type, long_varints=item.writer.long_varints)
        new_item.value = value
        item.item_pointers[item.writer.position] = (new_item, 0)
        item.writer.pack("<V", 0)  # global item fixup
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Creating new item and queuing data pack: {type(new_item.value).__name__}")

    def delayed_data_pack(_data_pack_queue) -> PackFileItem:
        new_item.start_writer()
        value.pack_packfile(new_item, value, existing_items, _data_pack_queue)
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing data for item: {type(new_item.value).__name__}")
        return new_item

    data_pack_queue.setdefault("pointer", deque()).append(delayed_data_pack)


def unpack_array(data_hk_type: tp.Type[hk], item: PackFileItem) -> list:
    array_pointer_offset = item.reader.position
    zero, array_size, array_capacity_and_flags = item.reader.unpack("<VII")
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"Array size: {array_size} | Capacity/Flags: {array_capacity_and_flags}")
    if zero != 0:
        print(f"Zero, array_size, array_caps_flags: {zero, array_size, array_capacity_and_flags}")
        print(f"Item child pointers: {item.child_pointers}")
        print(f"Item item pointers: {item.item_pointers}")
        print(f"Item raw data:\n{get_hex_repr(item.raw_data)}")
        raise AssertionError(f"Found non-null data at child pointer offset {hex(array_pointer_offset)}: {zero}")

    if array_size == 0:
        return []

    array_data_offset = item.child_pointers[array_pointer_offset]

    if debug.DEBUG_PRINT_UNPACK:
        debug.increment_debug_indent()
    with item.reader.temp_offset(array_data_offset):
        value = data_hk_type.unpack_primitive_array(item.reader, array_size)
        if value is None:
            # Array elements are tightly packed.
            value = [data_hk_type.unpack_packfile(item) for _ in range(array_size)]

    if debug.DEBUG_PRINT_UNPACK:
        debug.decrement_debug_indent()

    return value


def pack_array(
    array_hk_type: tp.Type[hkArray_],
    item: PackFileItem,
    value: list[hk | str | int | float | bool] | np.ndarray,
    existing_items: dict[hk, PackFileItem],
    data_pack_queue: dict[str, deque[tp.Callable]],
    with_flag=True,  # TODO: only found one array that doesn't use the flag (hkaBone["partitions"]).
):
    array_ptr_pos = item.writer.position
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"Array pointer position: {item.writer.position_hex} ({item.writer.long_varints})")
    item.writer.pack("<V", 0)  # where the fixup would go, if it was actually resolved
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"Array length position: {item.writer.position_hex}")
    item.writer.pack("<I", len(value))  # array length
    # Capacity is same as length, and highest bit is enabled (flags "do not free memory", I believe).
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"Array cap/flags position: {item.writer.position_hex}")
    item.writer.pack("<I", len(value) | (1 << 31 if with_flag else 0))  # highest bit on
    data_hk_type = array_hk_type.get_data_type()

    if len(value) == 0:
        return  # empty

    def delayed_data_write(_data_pack_queue):
        """Delayed writing of array data until later in the same packfile item."""

        _sub_data_pack_queue = {"pointer": deque(), "array_or_string": deque()}
        item.writer.pad_align(16)  # pre-align for array
        item.child_pointers[array_ptr_pos] = item.writer.position  # fixup
        array_start_offset = item.writer.position

        if not data_hk_type.try_pack_primitive_array(item.writer, value):
            # Non-primitive; recur on data type `pack` method.
            for i, element in enumerate(value):
                data_hk_type.pack_packfile(item, element, existing_items, _sub_data_pack_queue)
                item.writer.pad_to_offset(array_start_offset + (i + 1) * data_hk_type.byte_size)

        # Immediately recur on any new array/string data queued up (i.e., depth-first for packing arrays and strings).
        while _sub_data_pack_queue["array_or_string"]:
            _sub_data_pack_queue["array_or_string"].popleft()(_sub_data_pack_queue)
        # Pass on pointers to higher queue.
        while _sub_data_pack_queue["pointer"]:
            _data_pack_queue.setdefault("pointer", deque()).append(_sub_data_pack_queue["pointer"].popleft())

    data_pack_queue["array_or_string"].append(delayed_data_write)


def unpack_struct(
    data_hk_type: tp.Type[hk], item: PackFileItem, length: int
) -> tuple:
    """Identical to tagfile (just different recursive method)."""
    struct_start_offset = item.reader.position
    # TODO: Speed up for primitive types.
    return tuple(
        data_hk_type.unpack_packfile(
            item,
            offset=struct_start_offset + i * data_hk_type.byte_size,
        ) for i in range(length)
    )


def pack_struct(
    data_hk_type: tp.Type[hk],
    item: PackFileItem,
    value: tuple,
    existing_items: dict[hk, PackFileItem],
    data_pack_queue: dict[str, deque[tp.Callable]],
    length: int,
):
    """Structs are packed locally in the same item, but can contain pointers themselves."""
    struct_start_offset = item.writer.position
    # TODO: Speed up for primitive types.
    if len(value) != length:
        raise ValueError(f"Length of `{data_hk_type.__name__}` value is not {length}: {value}")
    for i, element in enumerate(value):
        item.writer.pad_to_offset(struct_start_offset + i * data_hk_type.byte_size)
        data_hk_type.pack_packfile(item, element, existing_items, data_pack_queue)


def unpack_string(item: PackFileItem) -> str:
    """Read a null-terminated string from item child pointer."""
    pointer_offset = item.reader.position
    item.reader.unpack_value("<V", asserted=0)
    try:
        string_offset = item.child_pointers[pointer_offset]
    except KeyError:
        return ""
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"Unpacking string at offset {hex(string_offset)}")
    string = item.reader.unpack_string(offset=string_offset, encoding="shift_jis_2004")
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"-> '{string}'")
    return string


def pack_string(
    item: PackFileItem,
    value: str,
    data_pack_queue: dict[str, deque[tp.Callable]],
    is_variant_name=False,
):
    """Note that string type (like `hkStringPtr`) is never explicitly defined in packfiles, since they do not have
    their own items, unlike in tagfiles."""
    string_ptr_pos = item.writer.position
    item.writer.pack("<V", 0)  # where fixup would be resolved

    if not value:
        return  # empty strings have no fixup

    def delayed_string_write(_item_creation_queue):
        item.child_pointers[string_ptr_pos] = item.writer.position
        item.writer.append(value.encode("shift_jis_2004") + b"\0")
        item.writer.pad_align(16)

    data_pack_queue.setdefault(
        "name_variant_string" if is_variant_name else "array_or_string",
        deque(),
    ).append(delayed_string_write)


def unpack_named_variant(
    hk_type: tp.Type[hk], item: PackFileItem, types_module: dict
) -> hk:
    """Detects `variant` type dynamically from `className` member."""
    member_start_offset = item.reader.position
    kwargs = {}
    # "variant" member type is a subclass of `hkReferencedObject` with name "className".
    name_member, class_name_member, variant_member = hk_type.members[:3]
    name = name_member.type.unpack_packfile(
        item, offset=member_start_offset + name_member.offset
    )
    kwargs[name_member.name] = name
    variant_type_name = class_name_member.type.unpack_packfile(
        item, offset=member_start_offset + class_name_member.offset
    )
    kwargs[class_name_member.name] = variant_type_name
    variant_py_name = get_py_name(variant_type_name)
    variant_type = types_module[variant_py_name]
    item.reader.seek(member_start_offset + variant_member.offset)
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"Unpacking named variant: {variant_py_name}... <{item.reader.position_hex}>")
        debug.increment_debug_indent()
    variant_instance = unpack_pointer(variant_type, item)
    if debug.DEBUG_PRINT_UNPACK:
        debug.decrement_debug_indent()
        debug.debug_print(f"--> {variant_instance}")
    kwargs[variant_member.name] = variant_instance

    # noinspection PyArgumentList
    instance = hk_type(**kwargs)

    return instance


def pack_named_variant(
    hk_type: tp.Type[hk],
    item: PackFileItem,
    value: hk,
    existing_items: dict[hk, PackFileItem],
    data_pack_queue: dict[str, deque[tp.Callable]],
):
    """TODO: Actually no different from `pack_class()`, because packfiles don't need `className` first."""
    member_start_offset = item.writer.position
    if debug.DEBUG_PRINT_UNPACK:
        debug.increment_debug_indent()

    name_member = hk_type.members[0]
    item.writer.pad_to_offset(member_start_offset + name_member.offset)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"Member 'name' (type `{name_member.type.__name__}`):")
    # `is_variant_name` not needed
    name_member.type.pack_packfile(item, value["name"], existing_items, data_pack_queue)

    class_name_member = hk_type.members[1]
    item.writer.pad_to_offset(member_start_offset + class_name_member.offset)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"Member 'className' (type `{class_name_member.type.__name__}`):")
    class_name_member.type.pack_packfile(item, value["className"], existing_items, data_pack_queue)

    variant_member = hk_type.members[2]
    item.writer.pad_to_offset(member_start_offset + variant_member.offset)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"Member 'variant' (type `{variant_member.type.__name__}`):")
    variant_member.type.pack_packfile(item, value["variant"], existing_items, data_pack_queue)

    if debug.DEBUG_PRINT_UNPACK:
        debug.decrement_debug_indent()
