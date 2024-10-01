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

import colorama
import numpy as np
from soulstruct_havok.types.debug import get_indented_array

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.packfile.structs import PackItemCreationQueues, PackFileDataItem
from .info import get_py_name

from . import debug

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryReader
    from .hk import hk
    from .base import hkArray_, Ptr_, hkRelArray_, hkViewPtr_

colorama.just_fix_windows_console()
G = colorama.Fore.GREEN
R = colorama.Fore.RED
Y = colorama.Fore.YELLOW
U = colorama.Fore.BLUE
C = colorama.Fore.CYAN
M = colorama.Fore.MAGENTA
X = colorama.Fore.RESET


def try_pad_to_offset(item: PackFileDataItem, offset: int, extra_msg: str):
    try:
        item.writer.pad_to_offset(offset)
    except ValueError:
        print(f"Item type: {item.hk_type.__name__}")
        print(extra_msg)
        raise


def unpack_bool(hk_type: type[hk], reader: BinaryReader) -> bool:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    value = reader.unpack_value(fmt) > 0
    if debug.DEBUG_PRINT_UNPACK and not debug.DO_NOT_DEBUG_PRINT_PRIMITIVES:
        debug.debug_print(f"{U}= {repr(value)}{X}")
    return value


def pack_bool(hk_type: type[hk], item: PackFileDataItem, value: bool):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"{Y}{item.hex}{X}: {G}{hk_type.get_type_name()}{X}{U} -> {value}{X}")
    item.writer.pack(fmt, int(value))


def unpack_int(hk_type: type[hk], reader: BinaryReader) -> int:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    value = reader.unpack_value(fmt)
    if debug.DEBUG_PRINT_UNPACK and not debug.DO_NOT_DEBUG_PRINT_PRIMITIVES:
        debug.debug_print(f"{U}= {repr(value)}{X}")
    return value


def pack_int(hk_type: type[hk], item: PackFileDataItem, value: int):
    """TODO: Had `signed = value < 0` here, but surely I can't just override the type restriction like that?"""
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"{Y}{item.hex}{X}: {G}{hk_type.get_type_name()}{X}{U} -> {value}{X}")
    item.writer.pack(fmt, value)


def unpack_float32(reader: BinaryReader) -> float | hk:
    """32-bit floats are unpacked directly; others (like half floats) are unpacked as classes (Havok's setup)."""
    value = reader.unpack_value("f")
    if debug.DEBUG_PRINT_UNPACK and not debug.DO_NOT_DEBUG_PRINT_PRIMITIVES:
        debug.debug_print(f"{U}= {repr(value)}{X}")
    return value


def pack_float(hk_type: type[hk], item: PackFileDataItem, value: float | hk):
    if hk_type.tag_type_flags == TagDataType.FloatAndFloat32:
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"{Y}{item.hex}{X}: {G}{hk_type.get_type_name()}{X}{U} -> {value}{X}")
        item.writer.pack("f", value)
    else:
        # Will definitely not use or create items.
        pack_class(hk_type, item, value, existing_items={}, data_pack_queues=None)


def unpack_class(hk_type: type[hk], item: PackFileDataItem) -> hk:
    """Main method for serialized Havok classes.

    Iterates over the class's members and unpacks them in order.

    NOTE: This is not used for `hkRootLevelContainerNamedVariant`, which uses a special dynamic unpacker to detect the
    appropriate `hkReferencedObject` subclass it points to with its `hkRefVariant` pointer.
    """
    kwargs = {}

    member_start_offset = item.reader.position
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"{Y}{item.hex}{X}: {C}<Class>{X} {G}{hk_type.get_type_name()}{X}")

    for member in hk_type.members:
        item_member_offset = member_start_offset + member.offset

        item_pos = item.reader.position
        if debug.DEBUG_PRINT_UNPACK and item_pos < item_member_offset:
            debug.debug_print(
                f"{Y}{item.hex}: {R}Space before member {M}{member.name}{X} "
                f"{R}({hex(item_pos - member_start_offset)} -> {hex(member.offset)}){X}"
            )

        if debug.DEBUG_PRINT_UNPACK:
            offset_hex = hex(member.offset)
            item_offset_hex = hex(item_member_offset)
            debug.debug_print(
                f"{Y}{item_offset_hex}: [{offset_hex}] {M}{member.name} {G}{member.type.__name__}{X}"
            )

        if item_pos > item_member_offset:
            # Member offsets must be incorrect in the class definition.
            raise ValueError(
                f"Item reader position ({hex(item_pos)}) is already "
                f"past member '{member.name}' offset {hex(item_member_offset)}."
            )

        if debug.DEBUG_PRINT_UNPACK:
            debug.increment_debug_indent()

        member_value = member.type.unpack_packfile(
            item,
            offset=member_start_offset + member.offset,
        )
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()
        kwargs[member.py_name] = member_value

    byte_size = hk_type.get_byte_size(item.long_varints)
    if item.reader.position < member_start_offset + byte_size:
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(
                f"{Y}{item.hex}: {R}Space after all members ({hex(item.reader.position - member_start_offset)} -> "
                f"{hex(byte_size)}){X}"
            )
        item.reader.seek(member_start_offset + byte_size)

    # noinspection PyArgumentList
    instance = hk_type(**kwargs)

    return instance


def pack_class(
    hk_type: type[hk],
    item: PackFileDataItem,
    value: hk,
    existing_items: dict[hk, PackFileDataItem],
    data_pack_queues: PackItemCreationQueues | None = None,
):
    """`data_pack_queues` can be `None` here for `float` classes packed as classes (with `value` member)."""
    members_start_offset = item.writer.position

    if "hkBaseObject" in [parent_type.__name__ for parent_type in hk_type.get_type_hierarchy()]:
        # Pointer for the mysterious base object type (probably a pointer to self).
        item.writer.pack("V", 0)

    if debug.DEBUG_PRINT_PACK:
        debug.increment_debug_indent()
    item.pending_rel_arrays.append(deque())
    for member in hk_type.members:
        # Member offsets may not be perfectly packed together, so we always pad up to the proper offset.
        # TODO: Of course, I'd love that to be false, and it really should be.
        try_pad_to_offset(
            item,
            members_start_offset + member.offset,
            f"{member.name} @ {hex(members_start_offset)} + {hex(member.offset)}",
        )
        member_value = value[member.name]
        if debug.DEBUG_PRINT_PACK:
            member_type_name = type(member_value).__name__
            debug.debug_print(
                f"{Y}{item.hex}: {M}{member.name} {G}{member_type_name} : {member.type.__name__}{X}"
            )
            debug.increment_debug_indent()
        # TODO: with_flag = member.name != "partitions" ?
        member.type.pack_packfile(item, member_value, existing_items, data_pack_queues)
        # TODO: Used to pad to member alignment here, but seems redundant.
        if debug.DEBUG_PRINT_PACK:
            debug.decrement_debug_indent()

    try_pad_to_offset(item, members_start_offset + hk_type.get_byte_size(item.long_varints), "End of class")
    if debug.DEBUG_PRINT_PACK:
        debug.decrement_debug_indent()

    # `hkRelArray` data is written after all members have been checked/written (before standard arrays/strings).
    for pending_rel_array in item.pending_rel_arrays.pop():
        pending_rel_array()


def unpack_pointer(data_hk_type: type[hk], item: PackFileDataItem) -> hk | None:
    """`data_hk_type` is used to make sure that the referenced item's `hk_type` is a subclass of it."""
    source_offset = item.reader.position
    zero = item.reader.unpack_value("V")  # "dummy" pointer
    if zero != 0:
        print(f"{item.hk_type.__name__} item pointers:")
        for offset, pointed_item in item.all_item_pointers.items():
            print(f"    Offset {hex(offset)} -> {pointed_item}")
        raise ValueError(f"Found non-zero value at item pointer offset {source_offset}: {zero}")

    try:
        pointed_item, item_data_offset = item.remaining_item_pointers.pop(source_offset)
    except KeyError:
        if source_offset not in item.all_item_pointers:
            return None  # null pointer (or incorrect member - no way to tell, but unused pointer should be found later)

        # Tried to access a pointer that was already used.
        print(f"{item.hk_type.__name__} item pointers:")
        for offset, pointed_item in item.all_item_pointers.items():
            print(f"    {R if offset == source_offset else X}{hex(offset)} -> {pointed_item}{X}")
        raise ValueError("Tried to use item pointer (in red) a second time.")

    if item_data_offset != 0:
        # Global item pointers always point to the start of the other item!
        print(f"{item.hk_type.__name__} item pointers:")
        for offset, pointed_item in item.all_item_pointers.items():
            print(f"    {R if offset == source_offset else X}{hex(offset)} -> {pointed_item}{X}")
        raise AssertionError(f"Data item pointer (global ref dest) was not zero: {item_data_offset}.")
    if not issubclass(pointed_item.hk_type, data_hk_type):
        item.print_item_dump()
        raise ValueError(
            f"Pointer-referenced item type {pointed_item.hk_type.__name__} is not a child of expected type "
            f"{data_hk_type.__name__}."
        )
    if pointed_item.value is None:
        # Unpack item (first time).
        if debug.DEBUG_PRINT_UNPACK:
            # Real item type is not known yet (could be a subclass of this reported type).
            debug.debug_print(f"{U}NEW ITEM: {pointed_item.hk_type.get_type_name()}{X}")
            if pointed_item.hk_type.get_type_name() in debug.DUMP_ITEMS:
                pointed_item.print_item_dump()
        pointed_item.start_reader()
        if debug.DEBUG_PRINT_UNPACK:
            debug.increment_debug_indent()
        # NOTE: `pointed_item.hk_type` may be a subclass of `data_hk_type`, so it's important we use it here.
        pointed_item.value = pointed_item.hk_type.unpack_packfile(pointed_item)
        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()

    else:
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"{M}Pointer to existing item: {pointed_item.get_class_name()}{X}")
    return pointed_item.value


def pack_pointer(
    ptr_hk_type: type[Ptr_] | type[hkRelArray_] | type[hkViewPtr_],
    item: PackFileDataItem,
    value: hk,
    existing_items: dict[hk, PackFileDataItem],
    data_pack_queues: PackItemCreationQueues,
):
    """Pointer to another item, which may or may not have already been created."""
    if value is None:
        # Null pointer. Item will not contain an item pointer here, and type will not appear in other HKX sections
        # (unless the same type has an instance elsewhere, of course).
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"{Y}{item.hex}: {G}{ptr_hk_type.__name__}{R} -> Null{X}")
        item.writer.pack("V", 0)
        return

    if value in existing_items:
        # Item has already been unpacked and previously referenced.
        item.all_item_pointers[item.writer.position] = (existing_items[value], 0)
        if debug.DEBUG_PRINT_PACK:
            existing_type_name = existing_items[value].get_class_name()  # may be subclass of `ptr_hk_type`
            debug.debug_print(f"{Y}{item.hex}: {G}{ptr_hk_type.__name__}{U} -> existing {existing_type_name}{X}")
        item.writer.pack("V", 0)  # dummy pointer
        return
    else:
        # NOTE: This uses the data type, NOT the `Ptr` type. Copies `long_varints` from source item.
        new_item = existing_items[value] = PackFileDataItem(
            hk_type=ptr_hk_type.get_data_type(),
            byte_order=item.byte_order,
            long_varints=item.long_varints,
            value=value,
        )
        item.all_item_pointers[item.writer.position] = (new_item, 0)
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"{Y}{item.hex}: {G}{new_item.get_class_name()}{U} -> new {new_item.get_class_name()}{X}")
        item.writer.pack("V", 0)  # dummy pointer

    def delayed_item_creation(_data_pack_queues: PackItemCreationQueues) -> PackFileDataItem:
        new_item.start_writer()
        if debug.DEBUG_PRINT_PACK:
            # Will have no indentation, as only the root packer loop calls this.
            debug.debug_print(f"{C}Starting item pack: {new_item.get_class_name()}{X}")
        value.pack_packfile(new_item, value, existing_items, _data_pack_queues)
        return new_item

    data_pack_queues.item_pointers.append(delayed_item_creation)


def unpack_array(data_hk_type: type[hk], item: PackFileDataItem) -> list:
    array_pointer_offset = item.reader.position
    zero, array_size, array_capacity_and_flags = item.reader.unpack("VII")
    color = R if array_capacity_and_flags != array_size | 0x80000000 else X
    if zero != 0:
        item.print_item_dump()
        raise ValueError(f"Found non-null data at child pointer offset {hex(array_pointer_offset)}: {zero}")

    if array_size == 0:
        if array_pointer_offset in item.all_child_pointers:
            item.print_item_dump()
            raise ValueError(f"Zero-size array has a child pointer fixup: {hex(array_pointer_offset)}")

        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(
                f"{Y}{array_pointer_offset}:{X} {M}{data_hk_type.get_type_name()}[0]{X} "
                f"{color}({hex(array_capacity_and_flags)}){X} {U}= []{X}"
            )
        return []

    try:
        array_data_offset = item.remaining_child_pointers.pop(array_pointer_offset)
    except KeyError:
        item.print_item_dump()
        raise ValueError(f"Array data offset not found in item child pointers: {array_pointer_offset}")

    # We step into the array data offset so that we can monitor expected member offsets.
    with item.reader.temp_offset(array_data_offset):
        value = data_hk_type.unpack_primitive_array(item.reader, array_size)
        if value is None:
            # Not a primitive array. Use data type. Array elements are tightly packed.
            if debug.DEBUG_PRINT_UNPACK:
                debug.debug_print(
                    f"{Y}{hex(array_data_offset)}: {M}{data_hk_type.get_type_name()}[{array_size}]{X} "
                    f"{color}({hex(array_capacity_and_flags)}){X}"
                )
                debug.increment_debug_indent()
            value = [data_hk_type.unpack_packfile(item) for _ in range(array_size)]
            if debug.DEBUG_PRINT_UNPACK:
                debug.decrement_debug_indent()

    if debug.DEBUG_PRINT_UNPACK:
        if len(value) > 10:
            value_repr = get_indented_array(value[:10]) if isinstance(value, np.ndarray) else repr(value[:10])
            debug.debug_print(f"{Y}{hex(array_pointer_offset)}: {U}{value_repr}...{X} ({len(value)} elements)")
        else:
            debug.debug_print(f"{Y}{hex(array_pointer_offset)}: {U}{repr(value)}{X}")

    return value


def pack_array(
    array_hk_type: tp.Type[hkArray_],
    item: PackFileDataItem,
    value: list[hk | str | int | float | bool] | np.ndarray,
    existing_items: dict[hk, PackFileDataItem],
    data_pack_queues: PackItemCreationQueues,
):
    array_pointer_offset = item.writer.position
    array_length = len(value)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(
            f"{Y}{item.hex}: {G}{array_hk_type.get_data_type().__name__}{C if array_length > 0 else R}[{array_length}] "
            f"{U if array_length > 0 else R}-> {'Child' if array_length > 0 else 'Null'}"
        )
    item.writer.pack("V", 0)  # where the fixup would go, if it was actually resolved
    item.writer.pack("I", array_length)
    capacity = array_hk_type.forced_capacity if array_hk_type.forced_capacity is not None else array_length
    item.writer.pack("I", capacity | array_hk_type.flags)
    data_hk_type = array_hk_type.get_data_type()

    if len(value) == 0:
        return  # empty

    def delayed_array_pack(_data_pack_queues: PackItemCreationQueues):
        """Delayed writing of array data until later in the same packfile item.

        This is the most complex part of the packfile algorithm because of how nested pointers and arrays/strings are
        handled. We use a 'depth first' approach for arrays/strings and a 'breadth-first' approach for pointers:
            - Any new arrays or strings will be packed as soon as this array finishes packing (which may include
            primitives, local `hk` classes, structs, etc. -- anything except pointers/arrays/strings).
            - Any new pointers are passed back up to the higher queue, which will be processed after this array's
            containing item is finished. *No items are written until the previous item finishes.*
        """

        sub_creation_queues = PackItemCreationQueues()
        item.writer.pad_align(16)  # pre-align for array
        item.all_child_pointers[array_pointer_offset] = item.writer.position  # fixup
        array_start_offset = item.writer.position

        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(
                f"{Y}{item.hex}{X}: {C}Array {array_hk_type.get_data_type().__name__}{C}[{array_length}]{X}"
            )

        if not data_hk_type.try_pack_primitive_array(item.writer, value):
            # Non-primitive; recur on data type `pack` method.
            if debug.DEBUG_PRINT_PACK:
                debug.increment_debug_indent()
            for i, element in enumerate(value):
                data_hk_type.pack_packfile(item, element, existing_items, sub_creation_queues)
                try_pad_to_offset(
                    item,
                    array_start_offset + (i + 1) * data_hk_type.get_byte_size(item.long_varints),
                    f"{item.get_class_name()} (Array) {data_hk_type.get_type_name()}[{i + 1}]",
                )
            if debug.DEBUG_PRINT_PACK:
                debug.decrement_debug_indent()

        # Immediately recur on any new array/string data queued up (i.e., depth-first for packing arrays and strings).
        while sub_creation_queues.child_pointers:
            if debug.DEBUG_PRINT_PACK:
                debug.increment_debug_indent()
            delayed_pack = sub_creation_queues.child_pointers.popleft()
            delayed_pack(sub_creation_queues)
            if debug.DEBUG_PRINT_PACK:
                debug.decrement_debug_indent()
        # Pass global item pointers to higher queue for later creation.
        while sub_creation_queues.item_pointers:
            delayed_item_creation = sub_creation_queues.item_pointers.popleft()
            _data_pack_queues.item_pointers.append(delayed_item_creation)

    data_pack_queues.child_pointers.append(delayed_array_pack)


def unpack_struct(
    data_hk_type: type[hk], item: PackFileDataItem, length: int
) -> tuple:
    """Identical to tagfile (just different recursive method)."""
    struct_start_offset = item.reader.position
    byte_size = data_hk_type.get_byte_size(item.long_varints)
    value = data_hk_type.unpack_primitive_array(item.reader, length)
    if value is None:
        # Recur on struct data type.
        value = tuple(
            data_hk_type.unpack_packfile(
                item,
                offset=struct_start_offset + i * byte_size,
            ) for i in range(length)
        )
    else:
        value = tuple(value)

    if debug.DEBUG_PRINT_UNPACK:
        if len(value) > 10:
            value_repr = get_indented_array(value[:10]) if isinstance(value, np.ndarray) else repr(value[:10])
            debug.debug_print(f"{Y}{hex(struct_start_offset)}: {U}{value_repr}...{X} ({len(value)} elements)")
        else:
            debug.debug_print(f"{Y}{hex(struct_start_offset)}: {U}{repr(value)}{X}")

    return tuple(value)


def pack_struct(
    data_hk_type: type[hk],
    item: PackFileDataItem,
    value: tuple | np.ndarray,
    existing_items: dict[hk, PackFileDataItem],
    data_pack_queues: PackItemCreationQueues,
    length: int,
):
    """Structs are packed locally in the same item, but can contain pointers themselves."""
    struct_start_offset = item.writer.position

    if isinstance(value, np.ndarray) and value.ndim > 1:
        # Flatten array.
        value = value.flatten()

    if len(value) != length:
        raise ValueError(f"Length of `{data_hk_type.__name__}` struct is not {length}: {value}")

    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"{Y}{item.hex}{X}: Struct {G}{data_hk_type.get_type_name()}[{length}]{U} -> {value}{X}")

    if not data_hk_type.try_pack_primitive_array(item.writer, value):
        # Non-primitive data type; recur on its `pack` method.
        byte_size = data_hk_type.get_byte_size(item.long_varints)
        for i, element in enumerate(value):
            try_pad_to_offset(
                item,
                struct_start_offset + i * byte_size,
                f"{item.get_class_name()} (Struct) {data_hk_type.get_type_name()}[{i}]",
            )
            data_hk_type.pack_packfile(item, element, existing_items, data_pack_queues)


def unpack_string(item: PackFileDataItem) -> str:
    """Read a null-terminated string from item child pointer."""
    pointer_offset = item.reader.position
    try:
        item.reader.unpack_value("V", asserted=0)
    except AssertionError:
        item.print_item_dump()
        raise ValueError(f"Non-zero found at expected string pointer offset: {pointer_offset}")
    try:
        string_offset = item.remaining_child_pointers.pop(pointer_offset)
    except KeyError:
        if pointer_offset not in item.all_child_pointers:
            # Empty string with no child pointer.
            return ""
        item.print_item_dump()
        raise ValueError(f"String data offset not found in item child pointers: {pointer_offset}")
    # We step into the offset so that we can monitor expected member offsets.
    string = item.reader.unpack_string(offset=string_offset, reset_old_offset=True, encoding="shift_jis_2004")
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"{Y}{hex(string_offset)}: {U}String = '{string}'{X}")
    return string


def pack_string(
    item: PackFileDataItem,
    value: str,
    data_pack_queues: PackItemCreationQueues,
):
    """Note that string type (like `hkStringPtr`) is never explicitly defined in packfiles, since they do not have
    their own items, unlike in tagfiles."""
    string_ptr_pos = item.writer.position
    item.writer.pack("V", 0)  # where fixup would be resolved

    if not value:
        return  # empty strings have no fixup

    def delayed_string_write(_data_pack_queues: PackItemCreationQueues):
        item.all_child_pointers[string_ptr_pos] = item.writer.position
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"{Y}{item.hex}{X}: {G}string {U}-> \"{value}\"{X}")
        item.writer.append(value.encode("shift_jis_2004") + b"\0")
        item.writer.pad_align(16)

    data_pack_queues.child_pointers.append(delayed_string_write)


def unpack_named_variant(hk_type: type[hk], item: PackFileDataItem, types_module: dict) -> hk:
    """Detects `variant` type dynamically from `className` member."""
    if debug.DEBUG_PRINT_UNPACK:
        debug.increment_debug_indent()

    member_start_offset = item.reader.position

    def _debug_print(member_):
        if debug.DEBUG_PRINT_UNPACK:
            offset_hex = hex(member_.offset)
            item_offset_hex = hex(member_start_offset + member_.offset)
            debug.debug_print(
                f"{Y}{item_offset_hex} ({offset_hex}){X}: {G}'{member_.name}' = {member_.type.__name__}{X}"
            )

    kwargs = {}
    # "variant" member type is a subclass of `hkReferencedObject` with name "className".
    name_member, class_name_member, variant_member = hk_type.members[:3]

    _debug_print(name_member)
    name = name_member.type.unpack_packfile(
        item, offset=member_start_offset + name_member.offset
    )
    kwargs[name_member.name] = name

    _debug_print(class_name_member)
    variant_type_name = class_name_member.type.unpack_packfile(
        item, offset=member_start_offset + class_name_member.offset
    )
    kwargs[class_name_member.name] = variant_type_name

    variant_py_name = get_py_name(variant_type_name)
    variant_type = types_module[variant_py_name]
    _debug_print(variant_member)
    item.reader.seek(member_start_offset + variant_member.offset)
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"{Y}{item.hex}: {U}Named Variant '{name}' = {variant_py_name}{X}")
    variant_instance = unpack_pointer(variant_type, item)
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"-> {variant_instance}")
        debug.decrement_debug_indent()
    kwargs[variant_member.name] = variant_instance

    # noinspection PyArgumentList
    instance = hk_type(**kwargs)

    return instance


def pack_named_variant(
    hk_type: type[hk],
    item: PackFileDataItem,
    value: hk,
    existing_items: dict[hk, PackFileDataItem],
    data_pack_queues: PackItemCreationQueues,
):
    """Actually no different from `pack_class()`, because packfiles don't write the `className` string first."""
    return pack_class(hk_type, item, value, existing_items, data_pack_queues)
