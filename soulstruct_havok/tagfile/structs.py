from __future__ import annotations

__all__ = ["TagFileItem"]

import logging
import typing as tp

from soulstruct_havok.enums import TagDataType

if tp.TYPE_CHECKING:
    from soulstruct.utilities.binary import BinaryWriter
    from soulstruct_havok.types.core import hk, hkArray_, Ptr_


_LOGGER = logging.getLogger(__name__)


class TagFileItem:
    """Analogous to `HKXDataEntry` in `packfile`-type HKX files. Appears in "ITEM" section of HKX tagfiles.

    HKX types are baked into these instances, rather than the usual reference index, because they are constructed only
    temporarily during tagfile unpack and pack.
    """

    hk_type: tp.Optional[tp.Type[hk]]
    value: tp.Optional[hk | bool | int | float | list | tuple]

    def __init__(
        self,
        hk_type: tp.Type[hk],  # may be a pointer or array
        absolute_offset=0,
        length=1,
        is_ptr=False,
        data=b"",
    ):
        self.hk_type = hk_type
        self.absolute_offset = absolute_offset
        self.length = length  # number of contained elements, NOT byte size (usually 1)
        self.is_ptr = is_ptr
        self.in_process = False  # prevents recursion
        self.value = None
        self.patches = {}  # type: dict[str, list[int]]  # maps type names to lists of offsets *IN THIS ITEM*

        self.writer = None  # type: tp.Optional[BinaryWriter]
        self.data = data  # for packing

    def finish_writer(self):
        if self.writer is None:
            raise ValueError(f"Tried to finish non-existent `writer` for item with type `{self.hk_type}`")
        self.data = self.writer.finish()
        self.writer = None  # ensure we don't accidentally try to write more

    def get_item_hk_type(self, hk_types_module):
        """Get actual data type of item (string, array, pointer, or `hkRootLevelContainer`)."""
        tag_data_type = self.hk_type.get_tag_data_type()
        if tag_data_type == TagDataType.CharArray:
            return getattr(hk_types_module, "_char")
        elif tag_data_type == TagDataType.Array:
            self.hk_type: hkArray_
            return self.hk_type.get_data_type()
        elif tag_data_type == TagDataType.Pointer:
            self.hk_type: Ptr_
            return type(self.value)
        elif self.hk_type.__name__ == "hkRootLevelContainer":
            return self.hk_type
        raise TypeError(f"`TagFileItem` is not a string, array, pointer, or hkRootLevelContainer: {self.hk_type.__name__}")

    def __repr__(self):
        return (
            f"TagFileItem:\n"
            f"        type = {self.hk_type.__name__ if self.hk_type else None}\n"
            # f"      offset = {self.absolute_offset}\n"
            f"      length = {self.length}\n"
            f"      is_ptr = {self.is_ptr}\n"
            f"       value = {self.value}"
        )
