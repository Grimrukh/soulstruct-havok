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

from collections import deque
from colorama import init as colorama_init, Fore
from soulstruct.utilities.binary import BinaryReader, BinaryWriter
from soulstruct.utilities.maths import Vector4

from soulstruct_havok.enums import TagDataType
from soulstruct_havok.tagfile.structs import TagFileItem
from .info import get_py_name

if tp.TYPE_CHECKING:
    from .hk import hk, HK_TYPE
    from .base import hkArray_, Ptr_, hkRelArray_, hkViewPtr_

_DEBUG_PRINT_UNPACK = False
_DEBUG_PRINT_PACK = False
_DO_NOT_DEBUG_PRINT_PRIMITIVES = True
_INDENT = 0
_REQUIRE_INPUT = False

colorama_init()


def SET_DEBUG_PRINT(unpack=False, pack=False):
    global _DEBUG_PRINT_UNPACK, _DEBUG_PRINT_PACK
    _DEBUG_PRINT_UNPACK = unpack
    _DEBUG_PRINT_PACK = pack


def increment_debug_indent():
    global _INDENT
    _INDENT += 4


def decrement_debug_indent():
    global _INDENT
    _INDENT -= 4


def debug_print(msg: tp.Any):
    print(" " * _INDENT + str(msg))


def unpack_bool(hk_type: tp.Type[hk], reader: BinaryReader) -> bool:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt) > 0


def pack_bool(hk_type: tp.Type[hk], item: TagFileItem, value: bool):
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    item.writer.pack(fmt, int(value))


def unpack_int(hk_type: tp.Type[hk], reader: BinaryReader) -> int:
    fmt = TagDataType.get_int_fmt(hk_type.tag_type_flags)
    return reader.unpack_value(fmt)


def pack_int(hk_type: tp.Type[hk], item: TagFileItem, value: int):
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


def unpack_class(hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem], instance=None) -> hk:
    """Existing `instance` created by caller can be passed, which is useful for managing recursion.

    NOTE: This is not used for `hkRootLevelContainerNamedVariant`, which uses a special dynamic unpacker to detect the
    appropriate `hkReferencedObject` subclass it points to with its `hkRefVariant` pointer.
    """
    kwargs = {}
    member_start_offset = reader.position

    if _DEBUG_PRINT_UNPACK:
        increment_debug_indent()
    for member in hk_type.members:
        if _DEBUG_PRINT_UNPACK:
            debug_print(f"Member '{member.name}' (type `{member.type.__name__}`):")
        member_value = member.type.unpack_tagfile(reader, member_start_offset + member.offset, items)
        if _DEBUG_PRINT_UNPACK:
            debug_print(f"    -> Real type: {type(member_value).__name__}")
        # TODO: For finding the floor material hex offset in map collisions.
        # if hk_type.__name__ == "_CustomMeshParameter":
        #     print(
        #         f"Custom mesh parameter member {member.name} offset: "
        #         f"{hex(member_start_offset + member.offset)} ({member_value})"
        #     )
        kwargs[member.name] = member_value  # type hint will be given in class definition
    decrement_debug_indent()
    if instance is None:
        # noinspection PyArgumentList
        instance = hk_type(**kwargs)
    else:
        for key, value in kwargs.items():
            setattr(instance, key, value)
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

    if _DEBUG_PRINT_UNPACK:
        increment_debug_indent()
    for member in hk_type.members:
        if _DEBUG_PRINT_PACK:
            debug_print(f"Member '{member.name}' (type `{member.type.__name__}`):")
        # Member offsets may not be perfectly packed together, so we always pad up to the proper offset.
        item.writer.pad_to_offset(member_start_offset + member.offset)
        member.type.pack_tagfile(item, value[member.name], items, existing_items, item_creation_queue)
    if _DEBUG_PRINT_UNPACK:
        decrement_debug_indent()

    item.writer.pad_to_offset(member_start_offset + hk_type.byte_size)


def unpack_pointer(data_hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem]) -> hk | None:
    item_index = reader.unpack_value("<I")
    if _DEBUG_PRINT_UNPACK:
        debug_print(f"`{data_hk_type.__name__}` pointer item index: {item_index}")
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
            item.value = item.hk_type.get_empty_instance()  # all member values are `None` but will be assigned below
            reader.seek(item.absolute_offset)
            unpack_class(item.hk_type, reader, items, instance=item.value)
        else:
            # No risk of recursion.
            item.value = item.hk_type.unpack_tagfile(reader, item.absolute_offset, items)
        item.in_process = False
    return item.value


def pack_pointer(
    ptr_hk_type: tp.Union[tp.Type[Ptr_], tp.Type[hkRelArray_], tp.Type[hkViewPtr_]],
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

    def delayed_item_creation(_item_creation_queue) -> None | TagFileItem:
        # Item may have been created since this function was queued.
        if value in existing_items:
            existing_item = existing_items[value]
            item.writer.pack_at(item_index_pos, "<I", items.index(existing_item))
            return None

        item.writer.pack_at(item_index_pos, "<I", len(items))
        value_data_hk_type = type(value)  # type: tp.Type[hk]  # may be a subclass of `data_hk_type`
        new_item = TagFileItem(ptr_hk_type, is_ptr=value_data_hk_type.get_tag_data_type() == TagDataType.Class)
        new_item.value = value
        existing_items[value] = new_item
        if _DEBUG_PRINT_PACK:
            debug_print(f"{Fore.YELLOW}Created item {len(items)}: {ptr_hk_type.__name__}{Fore.RESET}")
        items.append(new_item)
        new_item.writer = BinaryWriter()
        # Item does NOT recur `.pack_tagfile()` here. It is packed when this item is iterated over.
        return new_item

    item_creation_queue.setdefault("pointer", deque()).append(delayed_item_creation)


def unpack_array(data_hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem]) -> list:
    item_index = reader.unpack_value("<I")
    if _DEBUG_PRINT_UNPACK:
        debug_print(f"Array item index: {item_index} (type `{data_hk_type.__name__}`)")
    if item_index == 0:
        return []
    item = items[item_index]

    if item.value is None:
        if _DEBUG_PRINT_UNPACK:
            increment_debug_indent()

        # Check for primitive types and unpack all at once (rather than, eg, unpacking 10000 floats over 10000 calls).
        tag_data_type = data_hk_type.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            # Cannot unpack opaque type (and there shouldn't be anything to unpack in the file).
            item.value = [None] * item.length
        elif tag_data_type == TagDataType.Bool:
            fmt = TagDataType.get_int_fmt(data_hk_type.tag_type_flags, count=item.length)
            item.value = [v > 0 for v in reader.unpack(fmt, offset=item.absolute_offset)]
        elif tag_data_type == TagDataType.Int:
            fmt = TagDataType.get_int_fmt(data_hk_type.tag_type_flags, count=item.length)
            item.value = list(reader.unpack(fmt, offset=item.absolute_offset))
        elif data_hk_type.tag_type_flags == TagDataType.FloatAndFloat32:
            item.value = list(reader.unpack(f"<{item.length}f", offset=item.absolute_offset))
        elif data_hk_type.__name__ in {"hkVector4", "hkVector4f"}:
            # More efficient unpacking of this common basic data struct.
            vector_floats = list(reader.unpack(f"<{item.length * 4}f", offset=item.absolute_offset))
            item.value = [Vector4(vector_floats[i:i + 4]) for i in range(0, item.length * 4, 4)]
        else:  # non-primitive; recur on data type `unpack` method
            item.value = [
                data_hk_type.unpack_tagfile(
                    reader,
                    offset=item.absolute_offset + i * data_hk_type.byte_size,
                    items=items,
                ) for i in range(item.length)
            ]
        if _DEBUG_PRINT_UNPACK:
            decrement_debug_indent()
    return item.value


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
    data_hk_type = array_hk_type.get_data_type()  # type: HK_TYPE

    def delayed_item_creation(_item_creation_queue) -> TagFileItem:
        item.writer.pack_at(item_index_pos, "<I", len(items))
        new_item = TagFileItem(array_hk_type, is_ptr=False, length=len(value))
        item.patches.setdefault(new_item.hk_type.__name__, []).append(item_index_pos)
        new_item.value = value
        if _DEBUG_PRINT_PACK:
            debug_print(f"{Fore.YELLOW}Created item {len(items)}: hkArray[{data_hk_type.__name__}]{Fore.RESET}")
        items.append(new_item)
        new_item.writer = BinaryWriter()

        # For primitive types, tightly pack all at once.
        tag_data_type = data_hk_type.get_tag_data_type()
        if tag_data_type == TagDataType.Invalid:
            pass
        elif tag_data_type == TagDataType.Bool:
            fmt = TagDataType.get_int_fmt(data_hk_type.tag_type_flags, count=new_item.length)
            new_item.writer.pack(fmt, *[int(v) for v in value])
        elif tag_data_type == TagDataType.Int:
            fmt = TagDataType.get_int_fmt(data_hk_type.tag_type_flags, count=new_item.length)
            new_item.writer.pack(fmt, *value)
        elif data_hk_type.tag_type_flags == TagDataType.FloatAndFloat32:
            new_item.writer.pack(f"<{new_item.length}f", *value)
        else:  # non-primitive; recur on data type `pack` method
            for i, element in enumerate(value):
                data_hk_type.pack_tagfile(new_item, element, items, existing_items, _item_creation_queue)
                new_item.writer.pad_to_offset((i + 1) * data_hk_type.byte_size)
        return new_item

    item_creation_queue.setdefault("array", deque()).append(delayed_item_creation)
    if _DEBUG_PRINT_PACK:
        debug_print(f"{Fore.GREEN}Queued item creation: hkArray[{data_hk_type.__name__}]{Fore.RESET}")


def unpack_struct(
    data_hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem], length: int
) -> tuple:
    struct_start_offset = reader.position

    # Check for primitive types and unpack all at once (rather than, eg, unpacking 10000 floats over 10000 calls).
    # We can assume tight packing for these primitives (`data_hk_type.byte_size` is predictable).
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
        return reader.unpack(f"<{length}f")
    else:  # non-primitive; recur on data type `unpack` method (and do not assume tight packing)
        return tuple(
            data_hk_type.unpack_tagfile(
                reader,
                offset=struct_start_offset + i * data_hk_type.byte_size,
                items=items,
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

    # For primitive types, pack all at once (predictably tight for these primitives, so no need to pad).
    tag_data_type = data_hk_type.get_tag_data_type()
    if tag_data_type == TagDataType.Invalid:
        pass
    elif tag_data_type == TagDataType.Bool:
        fmt = TagDataType.get_int_fmt(data_hk_type.tag_type_flags, count=length)
        item.writer.pack(fmt, *[int(v) for v in value])
    elif tag_data_type == TagDataType.Int:
        fmt = TagDataType.get_int_fmt(data_hk_type.tag_type_flags, count=length)
        item.writer.pack(fmt, *value)
    elif data_hk_type.tag_type_flags == TagDataType.FloatAndFloat32:
        item.writer.pack(f"<{length}f", *value)
    else:  # non-primitive; recur on data type `pack` method
        for i, element in enumerate(value):
            item.writer.pad_to_offset(struct_start_offset + i * data_hk_type.byte_size)
            data_hk_type.pack_tagfile(item, element, items, existing_items, item_creation_queue)


def unpack_string(reader: BinaryReader, items: list[TagFileItem]) -> str:
    """Nothing more than an array of `char` bytes (standard `const char*`)."""
    item_index = reader.unpack_value("<I")
    if _DEBUG_PRINT_UNPACK:
        debug_print(f"String item index: {item_index}")
    if item_index == 0:
        return ""
    item = items[item_index]
    if item.value is None:
        reader.seek(item.absolute_offset)
        encoded = reader.read(item.length)
        item.value = encoded.decode("shift_jis_2004").rstrip("\0")
    return item.value


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
        item.writer.pack_at(item_index_pos, "<I", len(items))
        encoded = value.encode("shift_jis_2004") + b"\0"
        new_item = TagFileItem(string_hk_type, is_ptr=False, length=len(encoded))
        if _DEBUG_PRINT_PACK:
            debug_print(f"{Fore.YELLOW}Created item {len(items)}: {string_hk_type.__name__}{Fore.RESET}")
        new_item.value = value
        items.append(new_item)
        new_item.writer = BinaryWriter()
        new_item.writer.append(encoded)  # could write `data` immediately but this is more consistent
        return new_item

    if is_variant_name:
        if _DEBUG_PRINT_PACK:
            debug_print(
                f"{Fore.GREEN}Queued VARIANT NAME STRING: {string_hk_type.__name__} ({value}){Fore.RESET}"
            )
        item_creation_queue.setdefault("variant_name_string", deque()).append(delayed_item_creation)
    else:
        if _DEBUG_PRINT_PACK:
            debug_print(f"{Fore.GREEN}Queued string: {string_hk_type.__name__} ({value}){Fore.RESET}")
        item_creation_queue.setdefault("string", deque()).append(delayed_item_creation)


def unpack_named_variant(
    hk_type: tp.Type[hk], reader: BinaryReader, items: list[TagFileItem], types_module: dict
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
    if _DEBUG_PRINT_UNPACK:
        debug_print(f"Unpacking named variant: {hk_type.__name__}... <{reader.position_hex}>")
        increment_debug_indent()
    variant_instance = unpack_pointer(variant_type, reader, items)
    if _DEBUG_PRINT_UNPACK:
        decrement_debug_indent()
        debug_print(f"--> {variant_instance}")
    kwargs[variant_member.name] = variant_instance
    # noinspection PyArgumentList
    return hk_type(**kwargs)


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
    if _DEBUG_PRINT_UNPACK:
        increment_debug_indent()

    name_member = hk_type.members[0]
    item.writer.pad_to_offset(member_start_offset + name_member.offset)
    if _DEBUG_PRINT_PACK:
        debug_print(f"Member 'name' (type `{name_member.type.__name__}`):")
    pack_string(name_member.type, item, value["name"], items, item_creation_queue, is_variant_name=True)

    class_name_member = hk_type.members[1]
    item.writer.pad_to_offset(member_start_offset + class_name_member.offset)
    if _DEBUG_PRINT_PACK:
        debug_print(f"Member 'className' (type `{class_name_member.type.__name__}`):")
    class_name_member.type.pack_tagfile(item, value["className"], items, existing_items, item_creation_queue)

    variant_member = hk_type.members[2]
    item.writer.pad_to_offset(member_start_offset + variant_member.offset)
    if _DEBUG_PRINT_PACK:
        debug_print(f"Member 'variant' (type `{variant_member.type.__name__}`):")
    variant_member.type.pack_tagfile(item, value["variant"], items, existing_items, item_creation_queue)

    if _DEBUG_PRINT_UNPACK:
        decrement_debug_indent()
