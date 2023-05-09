from __future__ import annotations

__all__ = [
    "SET_DEBUG_PRINT",
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

from soulstruct.utilities.inspection import get_hex_repr
from soulstruct_havok.enums import TagDataType
from .info import get_py_name

if tp.TYPE_CHECKING:
    from collections import deque
    from soulstruct.utilities.binary import BinaryReader
    from soulstruct_havok.packfile.structs import PackFileItemEntry
    from .hk import hk
    from .base import hkArray_



def unpack_bool(hk_type: tp.Type[hk], reader: BinaryReader) -> bool:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt) > 0


def pack_bool(hk_type: tp.Type[hk], item: PackFileItemEntry, value: bool):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    item.writer.pack(fmt, int(value))


def unpack_int(hk_type: tp.Type[hk], reader: BinaryReader) -> int:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt)


def pack_int(hk_type: tp.Type[hk], item: PackFileItemEntry, value: int):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags, signed=value < 0)
    item.writer.pack(fmt, value)


def unpack_float32(reader: BinaryReader) -> float | hk:
    """32-bit floats are unpacked directly; others (like half floats) are unpacked as classes (Havok's setup)."""
    return reader.unpack_value("<f")


def pack_float(hk_type: tp.Type[hk], item: PackFileItemEntry, value: float | hk):
    if hk_type.tag_type_flags == TagDataType.Float | TagDataType.Float32:
        item.writer.pack("<f", value)
    else:
        # Will definitely not use or create items.
        pack_class(hk_type, item, value, existing_items={}, data_pack_queue={})


def unpack_class(hk_type: tp.Type[hk], entry: PackFileItemEntry, instance=None) -> hk:
    """Existing `instance` created by caller can be passed, which is useful for managing recursion.

    NOTE: This is not used for `hkRootLevelContainerNamedVariant`, which uses a special dynamic unpacker to detect the
    appropriate `hkReferencedObject` subclass it points to with its `hkRefVariant` pointer.
    """
    if instance is None:
        instance = hk_type()
    member_start_offset = entry.reader.position

    if _DEBUG_PRINT_UNPACK:
        hk.increment_debug_indent()
    for member in hk_type.members:
        if _DEBUG_PRINT_UNPACK:
            debug_print(
                f"Member '{member.name}' at offset {entry.reader.position_hex} (`{member.type.__name__}`):"
            )
        member_value = member.type.unpack_packfile(
            entry,
            offset=member_start_offset + member.offset,
        )
        setattr(instance, member.name, member_value)  # type hint will be given in class definition
    if _DEBUG_PRINT_UNPACK:
        decrement_debug_indent()
    return instance


def pack_class(
    hk_type: tp.Type[hk],
    item: PackFileItemEntry,
    value: hk,
    existing_items: dict[hk, PackFileItemEntry],
    data_pack_queue: dict[str, deque[tp.Callable]],
):
    member_start_offset = item.writer.position

    if "hkBaseObject" in [parent_type.__name__ for parent_type in hk_type.get_type_hierarchy()]:
        # Pointer for the mysterious base object type.
        item.writer.pack("<V", 0)

    if _DEBUG_PRINT_UNPACK:
        hk.increment_debug_indent()
    item.pending_rel_arrays.append(deque())
    for member in hk_type.members:
        if _DEBUG_PRINT_PACK:
            debug_print(
                f"Member '{member.name}' (type `{type(value[member.name]).__name__} : {member.type.__name__}`):"
            )
        # Member offsets may not be perfectly packed together, so we always pad up to the proper offset.
        item.writer.pad_to_offset(member_start_offset + member.offset)
        # TODO: with_flag = member.name != "partitions" ?
        member.type.pack_packfile(item, value[member.name], existing_items, data_pack_queue)
        # TODO: Used to pad to member alignment here, but seems redundant.
    item.writer.pad_to_offset(member_start_offset + hk_type.byte_size)
    if _DEBUG_PRINT_UNPACK:
        decrement_debug_indent()

    # `hkRelArray` data is written after all members have been checked/written.
    for pending_rel_array in item.pending_rel_arrays.pop():
        pending_rel_array()


def unpack_pointer(data_hk_type: tp.Type[hk], item: PackFileItemEntry) -> hk | None:
    """`data_hk_type` is used to make sure that the referenced entry's `hk_type` is a subclass of it."""
    source_offset = item.reader.position
    zero = item.reader.unpack_value("<V")  # "dummy" pointer
    try:
        pointed_item, item_data_offset = item.entry_pointers[source_offset]
    except KeyError:
        if zero != 0:
            print(zero, item.entry_pointers)
            raise ValueError(
                f"Could not find entry pointer: type {item.hk_type.__name__}, buffer at {hex(source_offset)}."
            )
        else:
            return None
    if zero != 0:
        raise AssertionError(f"Found non-zero data at entry pointer offset: {zero}.")
    if item_data_offset != 0:
        print(pointed_item.entry_pointers)
        raise AssertionError(f"Data entry pointer (global ref dest) was not zero: {item_data_offset}.")
    if not issubclass(pointed_item.hk_type, data_hk_type):
        raise ValueError(
            f"Pointer-referenced entry type {pointed_item.hk_type.__name__} is not a child of expected type "
            f"{data_hk_type.__name__}."
        )
    if pointed_item.value is None:
        # Unpack entry (first time).
        pointed_item.start_reader()
        if _DEBUG_PRINT_UNPACK:
            hk.increment_debug_indent()
        # NOTE: `pointed_item.hk_type` may be a subclass of `data_hk_type`, so it's important we use it here.
        pointed_item.value = pointed_item.hk_type.unpack_packfile(pointed_item)
        if _DEBUG_PRINT_UNPACK:
            decrement_debug_indent()
    else:
        if _DEBUG_PRINT_UNPACK:
            debug_print(f"Existing item: {type(pointed_item.value).__name__}")
    return pointed_item.value


def pack_pointer(
    data_hk_type: tp.Type[hk],
    item: PackFileItemEntry,
    value: hk,
    existing_items: dict[hk, PackFileItemEntry],
    data_pack_queue: dict[str, deque[tp.Callable]],
):
    if value is None:
        # Null pointer. Space is left for a global fixup, but it will never have a fixup.
        item.writer.pack("<V", 0)  # global item fixup
        return

    if value in existing_items:
        item.entry_pointers[item.writer.position] = (existing_items[value], 0)
        item.writer.pack("<V", 0)  # global item fixup
        if _DEBUG_PRINT_PACK:
            debug_print(f"Existing item: {type(existing_items[value]).__name__}")
        return
    else:
        # NOTE: This uses the data type, NOT the `Ptr` type.
        new_item = existing_items[value] = PackFileItemEntry(hk_type=data_hk_type)
        new_item.value = value
        item.entry_pointers[item.writer.position] = (new_item, 0)
        item.writer.pack("<V", 0)  # global item fixup
        if _DEBUG_PRINT_PACK:
            debug_print(f"Creating new item and queuing data pack: {type(new_item.value).__name__}")

    def delayed_data_pack(_data_pack_queue) -> PackFileItemEntry:
        new_item.start_writer()
        value.pack_packfile(new_item, value, existing_items, _data_pack_queue)
        if _DEBUG_PRINT_PACK:
            debug_print(f"Packing data for item: {type(new_item.value).__name__}")
        return new_item

    data_pack_queue.setdefault("pointer", deque()).append(delayed_data_pack)


def unpack_array(data_hk_type: tp.Type[hk], entry: PackFileItemEntry) -> list:
    array_pointer_offset = entry.reader.position
    zero, array_size, array_capacity_and_flags = entry.reader.unpack("<VII")
    if _DEBUG_PRINT_UNPACK:
        debug_print(f"Array size: {array_size} | Capacity/Flags: {array_capacity_and_flags}")
    if zero != 0:
        print(f"Zero, array_size, array_caps_flags: {zero, array_size, array_capacity_and_flags}")
        print(f"Entry child pointers: {entry.child_pointers}")
        print(f"Entry entry pointers: {entry.entry_pointers}")
        print(f"Entry raw data:\n{get_hex_repr(entry.raw_data)}")
        raise AssertionError(f"Found non-null data at child pointer offset {hex(array_pointer_offset)}: {zero}")

    if array_size == 0:
        return []

    array_data_offset = entry.child_pointers[array_pointer_offset]

    if _DEBUG_PRINT_UNPACK:
        hk.increment_debug_indent()
    with entry.reader.temp_offset(array_data_offset):
        # TODO: Speed up for primitive types.
        value = []
        for i in range(array_size):
            if _DEBUG_PRINT_UNPACK:
                debug_print(f"Unpacking array element {i} at entry reader position {entry.reader.position_hex}...")
                if data_hk_type.get_type_name() == "Ptr[hkpRigidBody]":
                    print(f"Entry other-entry pointers: {entry.entry_pointers}")
                    print(f"Next 0x8 bytes: {entry.reader.peek(8)}")
            value.append(
                data_hk_type.unpack_packfile(
                    entry,
                    # no offset needed, as array elements are tightly packed
                )
            )
            if _DEBUG_PRINT_UNPACK:
                debug_print(
                    f"Finished unpacking array element {i} at entry reader position {entry.reader.position_hex}..."
                )

    if _DEBUG_PRINT_UNPACK:
        decrement_debug_indent()

    return value


def pack_array(
    array_hk_type: tp.Type[hkArray_],
    item: PackFileItemEntry,
    value: list[hk | str | int | float | bool],
    existing_items: dict[hk, PackFileItemEntry],
    data_pack_queue: dict[str, deque[tp.Callable]],
    with_flag=True,  # TODO: only found one array that doesn't use the flag (hkaBone["partitions"]).
):
    array_ptr_pos = item.writer.position
    item.writer.pack("<V", 0)  # where the fixup would go, if it was actually resolved
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
        # TODO: Speed up for primitive types (bool/int/float).
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
    data_hk_type: tp.Type[hk], entry: PackFileItemEntry, length: int
) -> tuple:
    """Identical to tagfile (just different recursive method)."""
    struct_start_offset = entry.reader.position
    # TODO: Speed up for primitive types.
    print(entry.reader.position_hex)
    if data_hk_type.__name__ == "Ptr[hkpConstraintMotor]":
        print(entry.reader.peek(20))
        print(entry.entry_pointers)
    return tuple(
        data_hk_type.unpack_packfile(
            entry,
            offset=struct_start_offset + i * data_hk_type.byte_size,
        ) for i in range(length)
    )


def pack_struct(
    data_hk_type: tp.Type[hk],
    item: PackFileItemEntry,
    value: tuple,
    existing_items: dict[hk, PackFileItemEntry],
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


def unpack_string(entry: PackFileItemEntry) -> str:
    """Read a null-terminated string from entry child pointer."""
    pointer_offset = entry.reader.position
    entry.reader.unpack_value("<V", asserted=0)
    try:
        string_offset = entry.child_pointers[pointer_offset]
    except KeyError:
        return ""
    if _DEBUG_PRINT_UNPACK:
        debug_print(f"Unpacking string at offset {hex(string_offset)}")
    return entry.reader.unpack_string(offset=string_offset, encoding="shift_jis_2004")


def pack_string(
    item: PackFileItemEntry,
    value: str,
    data_pack_queue: dict[str, deque[tp.Callable]],
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

    data_pack_queue.setdefault("array_or_string", deque()).append(delayed_string_write)


def unpack_named_variant(
    hk_type: tp.Type[hk], item: PackFileItemEntry, types_module: dict
) -> hk:
    """Detects `variant` type dynamically from `className` member."""
    instance = hk_type()
    member_start_offset = item.reader.position
    # "variant" member type is a subclass of `hkReferencedObject` with name "className".
    name_member, class_name_member, variant_member = hk_type.members[:3]
    name = name_member.type.unpack_packfile(
        item, offset=member_start_offset + name_member.offset
    )
    setattr(instance, name_member.name, name)
    variant_type_name = class_name_member.type.unpack_packfile(
        item, offset=member_start_offset + class_name_member.offset
    )
    setattr(instance, class_name_member.name, variant_type_name)
    variant_py_name = get_py_name(variant_type_name)
    variant_type = types_module[variant_py_name]
    item.reader.seek(member_start_offset + variant_member.offset)
    if _DEBUG_PRINT_UNPACK:
        debug_print(f"Unpacking named variant: {hk_type.__name__}... <{item.reader.position_hex}>")
        hk.increment_debug_indent()
    variant_instance = unpack_pointer(variant_type, item)
    if _DEBUG_PRINT_UNPACK:
        decrement_debug_indent()
        debug_print(f"--> {variant_instance}")
    setattr(instance, variant_member.name, variant_instance)
    return instance


def pack_named_variant(
    hk_type: tp.Type[hk],
    item: PackFileItemEntry,
    value: hk,
    existing_items: dict[hk, PackFileItemEntry],
    data_pack_queue: dict[str, deque[tp.Callable]],
):
    """TODO: Actually no different from `pack_class()`, because packfiles don't need `className` first."""
    member_start_offset = item.writer.position
    if _DEBUG_PRINT_UNPACK:
        hk.increment_debug_indent()

    name_member = hk_type.members[0]
    item.writer.pad_to_offset(member_start_offset + name_member.offset)
    if _DEBUG_PRINT_PACK:
        debug_print(f"Member 'name' (type `{name_member.type.__name__}`):")
    # `is_variant_name` not needed
    name_member.type.pack_packfile(item, value["name"], existing_items, data_pack_queue)

    class_name_member = hk_type.members[1]
    item.writer.pad_to_offset(member_start_offset + class_name_member.offset)
    if _DEBUG_PRINT_PACK:
        debug_print(f"Member 'className' (type `{class_name_member.type.__name__}`):")
    class_name_member.type.pack_packfile(item, value["className"], existing_items, data_pack_queue)

    variant_member = hk_type.members[2]
    item.writer.pad_to_offset(member_start_offset + variant_member.offset)
    if _DEBUG_PRINT_PACK:
        debug_print(f"Member 'variant' (type `{variant_member.type.__name__}`):")
    variant_member.type.pack_packfile(item, value["variant"], existing_items, data_pack_queue)

    if _DEBUG_PRINT_UNPACK:
        decrement_debug_indent()
