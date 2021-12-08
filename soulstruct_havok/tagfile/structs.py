from __future__ import annotations

__all__ = ["TagFileItem"]

import logging
import typing as tp

if tp.TYPE_CHECKING:
    from soulstruct_havok.types_base import hk


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
        hk_type: tp.Type[hk],
        absolute_offset=0,
        length=0,
        is_ptr=False,
        data=b"",
    ):
        self.hk_type = hk_type
        self.absolute_offset = absolute_offset
        self.length = length
        self.is_ptr = is_ptr
        self.in_process = False  # prevents recursion
        self.value = None

        self.data = data  # for packing

    def __repr__(self):
        return (
            f"TagFileItem:\n"
            f"        type = {self.hk_type.__name__ if self.hk_type else None}\n"
            f"      offset = {self.absolute_offset}\n"
            f"      length = {self.length}\n"
            f"      is_ptr = {self.is_ptr}\n"
            f"       value = {self.value}"
        )
