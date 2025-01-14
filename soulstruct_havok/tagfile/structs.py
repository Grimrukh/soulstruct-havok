from __future__ import annotations

__all__ = ["TagItemCreationQueues", "TagFileItem"]

import logging
import typing as tp
from collections import deque
from dataclasses import dataclass, field

from soulstruct.utilities.binary import BinaryWriter, ByteOrder

from soulstruct_havok.enums import TagDataType

if tp.TYPE_CHECKING:
    import numpy as np
    from soulstruct_havok.types.hk import hk, HK_TYPE


_LOGGER = logging.getLogger("soulstruct_havok")


@dataclass(slots=True)
class TagItemCreationQueues:
    # Byte order for item writers.
    byte_order: ByteOrder
    pointers: deque[tp.Callable[[TagItemCreationQueues], TagFileItem]] = field(default_factory=deque)
    arrays: deque[tp.Callable[[TagItemCreationQueues], TagFileItem]] = field(default_factory=deque)
    # These take precedence over other strings, for some reason.
    variant_name_strings: deque[tp.Callable[[TagItemCreationQueues], TagFileItem]] = field(default_factory=deque)
    strings: deque[tp.Callable[[TagItemCreationQueues], TagFileItem]] = field(default_factory=deque)

    def any(self):
        """Check if any of the queues have items."""
        return any((self.pointers, self.arrays, self.variant_name_strings, self.strings))


@dataclass(slots=True)
class TagFileItem:
    """Analogous to `PackFileItem` in `packfile`-type HKX files. Appears in "ITEM" section of HKX tagfiles.

    HKX types are baked into these instances, rather than the usual reference index, because they are constructed only
    temporarily during tagfile unpack and pack.
    """

    hk_type: HK_TYPE | None  # may be a pointer or array
    absolute_offset: int = 0
    length: int = 1
    is_ptr: bool = False  # true for `hk` instance pointers, false for everything else (arrays, strings)
    data: bytes = b""  # for packing
    value: hk | bool | int | float | list | tuple | str | np.ndarray | None = None
    patches: dict[str, list[int]] = field(default_factory=dict)  # maps type names to lists of offsets *IN THIS ITEM*

    writer: BinaryWriter | None = None
    in_process: bool = False  # prevents recursion

    def finish_writer(self):
        if self.writer is None:
            raise ValueError(f"Tried to finish non-existent `writer` for item with type `{self.hk_type}`")
        self.data = bytes(self.writer)
        self.writer = None  # ensure we don't accidentally try to write more

    def get_item_hk_data_type(self) -> HK_TYPE:
        """Get actual data type of item (string, array, pointer, or `hkRootLevelContainer`)."""
        if self.hk_type is None:
            raise ValueError("Tried to get item type before setting it.")
        tag_data_type = self.hk_type.get_tag_data_type()
        if tag_data_type == TagDataType.CharArray:
            # noinspection PyUnresolvedReferences
            return self.hk_type.get_data_type()
        elif tag_data_type == TagDataType.Array:  # hkArray_
            # noinspection PyUnresolvedReferences
            return self.hk_type.get_data_type()
        elif tag_data_type == TagDataType.Pointer:  # Ptr_
            return type(self.value)
        elif self.hk_type.__name__ == "hkRootLevelContainer":
            return self.hk_type
        raise TypeError(
            f"`TagFileItem` is not a string, array, pointer, or `hkRootLevelContainer`: {self.hk_type.__name__}"
        )

    def __repr__(self):
        return (
            f"TagFileItem:\n"
            f"        type = {self.hk_type.__name__ if self.hk_type else None}\n"
            # f"      offset = {self.absolute_offset}\n"
            f"      length = {self.length}\n"
            f"      is_ptr = {self.is_ptr}\n"
            f"       value = {self.value}"
        )
