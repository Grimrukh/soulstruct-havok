"""Functions for unpacking and packing Havok data in tagfiles."""
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

import colorama
import numpy as np

from soulstruct.utilities.binary import BinaryReader, BinaryWriter

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.tagfile.structs import TagItemCreationQueues, TagFileItem
from .info import get_py_name

from . import debug

if tp.TYPE_CHECKING:
    from .hk import hk, HK_TYPE
    from .base import hkArray_, Ptr_, hkRelArray_, hkViewPtr_


colorama.just_fix_windows_console()
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
YELLOW = colorama.Fore.YELLOW
BLUE = colorama.Fore.BLUE
CYAN = colorama.Fore.CYAN
MAGENTA = colorama.Fore.MAGENTA
RESET = colorama.Fore.RESET


def try_pad_to_offset(item: TagFileItem, offset: int, extra_msg: str):
    try:
        item.writer.pad_to_offset(offset)
    except ValueError:
        print(f"Item type: {item.hk_type.__name__}")
        print(extra_msg)
        raise


def unpack_bool(hk_type: type[hk], reader: BinaryReader) -> bool:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt) > 0


def pack_bool(hk_type: type[hk], item: TagFileItem, value: bool):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    item.writer.pack(fmt, int(value))


def unpack_int(hk_type: type[hk], reader: BinaryReader) -> int:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt)


def pack_int(hk_type: type[hk], item: TagFileItem, value: int):
    """TODO: Had `signed = value < 0` here, but surely I can't just override the type restriction like that?"""
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    item.writer.pack(fmt, value)


def unpack_float32(reader: BinaryReader) -> float | hk:
    """32-bit floats are unpacked directly; others (like half floats) are unpacked as classes (Havok's setup)."""
    return reader.unpack_value("f")


def pack_float(hk_type: type[hk], item: TagFileItem, value: float | hk):
    if hk_type.tag_type_flags == TagDataType.FloatAndFloat32:  # not `TagDataType.Class`
        item.writer.pack("f", value)
        return

    # Will definitely not point to or create items (probably just a lone integer `value` member to pack).
    pack_class(hk_type, item, value, items=[], existing_items={}, item_creation_queues=None)


def unpack_class(hk_type: type[hk], reader: BinaryReader, items: list[TagFileItem], instance=None) -> hk:
    """Existing `instance` created by caller can be passed, which is useful for managing recursion.

    NOTE: This is not used for `hkRootLevelContainerNamedVariant`, which uses a special dynamic unpacker to detect the
    appropriate `hkReferencedObject` subclass it points to with its `hkRefVariant` pointer.

    NOTE: Some Havok member names start with numbers, which is invalid in Python. These are renamed in the `hk` class
    definitions to start with an underscore.
    """
    kwargs = {}
    member_start_offset = reader.position

    if debug.DEBUG_PRINT_UNPACK:
        debug.increment_debug_indent()
    for member in hk_type.members:
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Member '{member.name}' (type `{member.type.__name__}`):")
        member_value = member.type.unpack_tagfile(reader, member_start_offset + member.offset, items)
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"    -> Real type: {type(member_value).__name__}")
        kwargs[member.py_name] = member_value  # type hint will be given in class definition
    if debug.DEBUG_PRINT_UNPACK:
        debug.decrement_debug_indent()
    if instance is None:
        # noinspection PyArgumentList
        instance = hk_type(**kwargs)
    else:
        for key, value in kwargs.items():
            setattr(instance, key, value)
    return instance


def pack_class(
    hk_type: type[hk],
    item: TagFileItem,
    value: hk,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queues: TagItemCreationQueues = None,
):
    member_start_offset = item.writer.position

    if debug.DEBUG_PRINT_PACK:
        debug.increment_debug_indent()
    for member in hk_type.members:
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Member '{member.name}' (type `{member.type.__name__}`):")
        # Member offsets may not be perfectly packed together, so we always pad up to the proper offset.
        item.writer.pad_to_offset(member_start_offset + member.offset)
        member.type.pack_tagfile(item, value[member.name], items, existing_items, item_creation_queues)
    if debug.DEBUG_PRINT_PACK:
        debug.decrement_debug_indent()

    item.writer.pad_to_offset(member_start_offset + hk_type.get_byte_size(True))


def unpack_pointer(data_hk_type: type[hk], reader: BinaryReader, items: list[TagFileItem]) -> hk | None:
    item_index = reader.unpack_value("I")
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"`{data_hk_type.__name__}` pointer item index: {item_index}")
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
            if item.hk_type.get_tag_data_type() != TagDataType.Class:
                raise AssertionError(f"Found item recursion inside non-class `{item.hk_type.__name__}`.")
        item.in_process = True
        is_named_variant = item.hk_type.__name__ == "hkRootLevelContainerNamedVariant"
        if item.hk_type.get_tag_data_type() == TagDataType.Class and not is_named_variant:
            # Create and assign instance to item here, before unpacker unpacks its members, so recursive views to
            # it can be assigned to the right instance (as `item.value` will not be None next time).
            item.value = item.hk_type.get_empty_instance()  # all member values are `None` but will be assigned below
            reader.seek(item.absolute_offset)
            unpack_class(item.hk_type, reader, items, instance=item.value)
        else:
            # No risk of recursion.
            item.value = item.hk_type.unpack_tagfile(reader, item.absolute_offset, items)
        item.in_process = False
    return item.value


def pack_pointer(
    ptr_hk_type: type[Ptr_] | type[hkRelArray_] | type[hkViewPtr_],
    item: TagFileItem,
    value: hk,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queues: TagItemCreationQueues,
):
    if value is None:
        # Null pointer (i.e. member value is `None`).
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"Packing {MAGENTA}`{ptr_hk_type.__name__}` = <nullptr>{RESET}")
        item.writer.pack("I", 0)
        return

    item.patches.setdefault(ptr_hk_type.__name__, []).append(item.writer.position)

    data_hk_type = ptr_hk_type.get_data_type()

    if not isinstance(value, data_hk_type):
        raise TypeError(
            f"Pointer to `{data_hk_type.get_type_name()}` contained wrong type: `{value.get_type_name()}`"
        )

    # Queues up a function that will create the item and write its offset to this position.
    # No need to reserve an index in the writer; it will be recorded in the function body.

    item.writer.reserve("ptr_offset", "I", obj=value)

    def delayed_item_creation(_item_creation_queues: TagItemCreationQueues) -> None | TagFileItem:
        # Item may have been created since this function was queued.
        if value in existing_items:
            existing_item = existing_items[value]
            item.writer.fill("ptr_offset", items.index(existing_item), obj=value)
            return None

        # Create new `TagFileItem`.
        item.writer.fill("ptr_offset", len(items), obj=value)
        value_data_hk_type = type(value)  # type: type[hk]  # may be a subclass of `data_hk_type`
        new_item = TagFileItem(
            hk_type=ptr_hk_type,
            is_ptr=value_data_hk_type.get_tag_data_type() == TagDataType.Class,
            value=value,
            writer=BinaryWriter(byte_order=_item_creation_queues.byte_order),
        )
        existing_items[value] = new_item
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"{YELLOW}Created item {len(items)}: {ptr_hk_type.__name__}{RESET}")
        items.append(new_item)
        # Item does NOT recur `.pack_tagfile()` here. It is packed whenever this item is iterated over.
        return new_item

    item_creation_queues.pointers.append(delayed_item_creation)


def unpack_array(data_hk_type: type[hk], reader: BinaryReader, items: list[TagFileItem]) -> list:
    item_index = reader.unpack_value("I")
    if item_index == 0:
        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Empty array (type `{data_hk_type.__name__}`)")
        return []
    item = items[item_index]

    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(
            f"Array item index: {item_index} (type `{data_hk_type.__name__}`) (data offset {hex(item.absolute_offset)})"
        )

    if item.value is None:
        if debug.DEBUG_PRINT_UNPACK:
            debug.increment_debug_indent()

        if debug.DEBUG_PRINT_UNPACK:
            debug.debug_print(f"Array data offset: {hex(item.absolute_offset)}")

        primitive_array = data_hk_type.unpack_primitive_array(reader, item.length, item.absolute_offset)
        if primitive_array is not None:
            item.value = primitive_array
        else:
            # Non-primitive; recur on data type `unpack` method.
            item.value = [
                data_hk_type.unpack_tagfile(
                    reader,
                    offset=item.absolute_offset + i * data_hk_type.get_byte_size(True),
                    items=items,
                ) for i in range(item.length)
            ]

        if debug.DEBUG_PRINT_UNPACK:
            debug.decrement_debug_indent()

    if len(item.value) > 10 and isinstance(item.value[0], (int, float)):
        debug.debug_print(f"= {repr(item.value[:10])}... ({len(item.value)} elements)")
    else:
        debug.debug_print(f"= {repr(item.value)}")

    return item.value


def pack_array(
    array_hk_type: tp.Type[hkArray_],
    item: TagFileItem,
    value: list[hk | str | int | float | bool] | np.ndarray,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queues: TagItemCreationQueues,
):
    """Array items are always created per instance, never re-used. (Not sure if that's correct, but it is here.)

    Note that array no longer writes its capacity/flags to the serialized HKX tagfile. It's just an offset to the array
    data, which is now in a separate item rather than a local 'child' of the same item.
    """
    if len(value) == 0:
        item.writer.pack("I", 0)
        return

    item.patches.setdefault(array_hk_type.get_type_name()).append(item.writer.position)
    item.writer.reserve("array_offset", "I", obj=value)
    data_hk_type = array_hk_type.get_data_type()  # type: HK_TYPE

    def delayed_item_creation(_item_creation_queues) -> TagFileItem:
        item.writer.fill("array_offset", len(items), obj=value)
        new_item = TagFileItem(
            hk_type=array_hk_type,
            is_ptr=False,
            length=len(value),
            value=value,
            writer=BinaryWriter(byte_order=_item_creation_queues.byte_order),
        )
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"{YELLOW}Created item {len(items)}: hkArray[{data_hk_type.__name__}]{RESET}")
        items.append(new_item)

        # Try primitive pack, then fall back to recursive pack.
        if not data_hk_type.try_pack_primitive_array(new_item.writer, value):
            # Non-primitive; recur on data type `pack` method.
            byte_size = data_hk_type.get_byte_size(True)
            for i, element in enumerate(value):
                data_hk_type.pack_tagfile(new_item, element, items, existing_items, _item_creation_queues)
                new_item.writer.pad_to_offset((i + 1) * byte_size)

        return new_item

    item_creation_queues.arrays.append(delayed_item_creation)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"{GREEN}Queued item creation: hkArray[{data_hk_type.__name__}]{RESET}")


def unpack_struct(
    data_hk_type: type[hk], reader: BinaryReader, items: list[TagFileItem], length: int
) -> tuple:
    """'Structs' (really fixed-length local arrays, e.g. `int[4]`) are packed locally in the item."""
    struct_start_offset = reader.position

    # Check for primitive types and unpack all at once (rather than, eg, unpacking 10000 floats over 10000 calls).
    # We can assume tight packing for these primitives (`data_hk_type.get_byte_size()` is predictable).
    tag_data_type = data_hk_type.get_tag_data_type()
    if tag_data_type == TagDataType.Invalid:
        # Cannot unpack opaque type (and there shouldn't be anything to unpack in the file).
        return (None,) * length
    elif tag_data_type == TagDataType.Bool:
        fmt = TagDataType.get_int_fmt(data_hk_type.tag_type_flags, count=length)
        return tuple(v > 0 for v in reader.unpack(fmt))
    elif tag_data_type == TagDataType.Int:
        fmt = TagDataType.get_int_fmt(data_hk_type.tag_type_flags, count=length)
        return reader.unpack(fmt)
    elif data_hk_type.tag_type_flags == TagDataType.FloatAndFloat32:
        return reader.unpack(f"{length}f")
    else:  # non-primitive; recur on data type `unpack` method (and do not assume tight packing)
        byte_size = data_hk_type.get_byte_size(True)
        return tuple(
            data_hk_type.unpack_tagfile(
                reader,
                offset=struct_start_offset + i * byte_size,
                items=items,
            ) for i in range(length)
        )


def pack_struct(
    data_hk_type: type[hk],
    item: TagFileItem,
    value: tuple | np.ndarray,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queues: TagItemCreationQueues,
    length: int,
):
    """Structs are packed locally in the same item, but can contain pointers themselves."""
    struct_start_offset = item.writer.position

    if isinstance(value, np.ndarray) and value.ndim > 1:
        # Flatten array.
        value = value.flatten()

    if len(value) != length:
        raise ValueError(f"Length of `{data_hk_type.__name__}` struct is not {length}: {value}")

    # For primitive types, pack all at once (predictably tight for these primitives, so no need to pad).
    if not data_hk_type.try_pack_primitive_array(item.writer, value):
        # Non-primitive data type; recur on its `pack` method.
        byte_size = data_hk_type.get_byte_size(True)
        for i, element in enumerate(value):
            item.writer.pad_to_offset(struct_start_offset + i * byte_size)
            data_hk_type.pack_tagfile(item, element, items, existing_items, item_creation_queues)


def unpack_string(reader: BinaryReader, items: list[TagFileItem]) -> str:
    """Nothing more than an array of `char` bytes (standard `const char*`)."""
    item_index = reader.unpack_value("I")
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"String item index: {item_index}")
    if item_index == 0:
        return ""
    item = items[item_index]
    if item.value is None:
        # First-time read (probably every time for strings as they're not reused).
        reader.seek(item.absolute_offset)
        encoded = reader.read(item.length)
        item.value = encoded.decode("shift_jis_2004").rstrip("\0")
    return item.value


def pack_string(
    string_hk_type: type[hk],
    item: TagFileItem,
    value: str,
    items: list[TagFileItem],
    item_creation_queues: TagItemCreationQueues,
    is_variant_name=False,
):
    """Like arrays (which they are, essentially), strings are never re-used as items."""
    item.patches.setdefault(string_hk_type.__name__, []).append(item.writer.position)

    if not value:
        # Empty string.
        item.writer.pack("I", 0)
        return
    if not isinstance(value, str):
        raise ValueError(f"Cannot pack non-string: {value}")

    item.writer.reserve("str_offset", "I", obj=value)

    def delayed_item_creation(_item_creation_queues) -> TagFileItem:
        item.writer.fill("str_offset", len(items), obj=value)
        encoded = value.encode("shift_jis_2004") + b"\0"
        new_item = TagFileItem(
            hk_type=string_hk_type,
            is_ptr=False,
            length=len(encoded),
            value=value,
            writer=BinaryWriter(byte_order=_item_creation_queues.byte_order),
        )
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"{YELLOW}Created item {len(items)}: {string_hk_type.__name__}{RESET}")
        items.append(new_item)
        new_item.writer.append(encoded)  # could write `data` immediately but this is more consistent
        return new_item

    if is_variant_name:
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(
                f"{GREEN}Queued VARIANT NAME STRING: {string_hk_type.__name__} ({value}){RESET}"
            )
        item_creation_queues.variant_name_strings.append(delayed_item_creation)
    else:
        if debug.DEBUG_PRINT_PACK:
            debug.debug_print(f"{GREEN}Queued string: {string_hk_type.__name__} ({value}){RESET}")
        item_creation_queues.strings.append(delayed_item_creation)


def unpack_named_variant(
    hk_type: type[hk], reader: BinaryReader, items: list[TagFileItem], types_module: dict
) -> hk:
    """Detects `variant` type dynamically from `className` member."""
    kwargs = {}
    member_start_offset = reader.position
    # "variant" member type is a subclass of `hkReferencedObject` with name "className".
    name_member, class_name_member, variant_member = hk_type.members[:3]
    name = name_member.type.unpack_tagfile(
        reader, member_start_offset + name_member.offset, items
    )
    kwargs[name_member.name] = name
    variant_type_name = class_name_member.type.unpack_tagfile(
        reader, member_start_offset + class_name_member.offset, items
    )
    kwargs[class_name_member.name] = variant_type_name
    variant_py_name = get_py_name(variant_type_name)
    variant_type = types_module[variant_py_name]
    reader.seek(member_start_offset + variant_member.offset)
    if debug.DEBUG_PRINT_UNPACK:
        debug.debug_print(f"Unpacking named variant: {hk_type.__name__}... <{reader.position_hex}>")
        debug.increment_debug_indent()
    variant_instance = unpack_pointer(variant_type, reader, items)
    if debug.DEBUG_PRINT_UNPACK:
        debug.decrement_debug_indent()
        debug.debug_print(f"--> {variant_instance}")
    kwargs[variant_member.name] = variant_instance
    # noinspection PyArgumentList
    return hk_type(**kwargs)


def pack_named_variant(
    hk_type: type[hk],
    item: TagFileItem,
    value: hk,
    items: list[TagFileItem],
    existing_items: dict[hk, TagFileItem],
    item_creation_queues: TagItemCreationQueues,
):
    """NOTE: Named variants create items for their 'name' members before their 'className' members.

    We handle this with a special subqueue for variant name strings.
    """
    member_start_offset = item.writer.position
    if debug.DEBUG_PRINT_PACK:
        debug.increment_debug_indent()

    name_member = hk_type.members[0]
    item.writer.pad_to_offset(member_start_offset + name_member.offset)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"Member 'name' (type `{name_member.type.__name__}`):")
    pack_string(name_member.type, item, value["name"], items, item_creation_queues, is_variant_name=True)

    class_name_member = hk_type.members[1]
    item.writer.pad_to_offset(member_start_offset + class_name_member.offset)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"Member 'className' (type `{class_name_member.type.__name__}`):")
    class_name_member.type.pack_tagfile(item, value["className"], items, existing_items, item_creation_queues)

    variant_member = hk_type.members[2]
    item.writer.pad_to_offset(member_start_offset + variant_member.offset)
    if debug.DEBUG_PRINT_PACK:
        debug.debug_print(f"Member 'variant' (type `{variant_member.type.__name__}`):")
    variant_member.type.pack_tagfile(item, value["variant"], items, existing_items, item_creation_queues)

    if debug.DEBUG_PRINT_PACK:
        debug.decrement_debug_indent()
