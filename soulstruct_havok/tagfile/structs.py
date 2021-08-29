from __future__ import annotations

__all__ = ["HKXItem"]

import typing as tp

from ..enums import TagDataType

if tp.TYPE_CHECKING:
    from ..nodes import HKXNode
    from ..types import HKXType


class HKXItem:
    """Analogous to `HKXDataEntry` in `packfile`-type HKX files. Appears in "ITEM" section of HKX tagfiles.

    HKX types are baked into these instances, rather than the usual reference index, because they are constructed only
    temporarily during tagfile unpack and pack.
    """

    hkx_type: tp.Optional[HKXType]
    node_value: tp.Union[None, list[HKXNode], list[bool], list[int], list[float], tuple[bool], tuple[int], tuple[float]]
    data_type: TagDataType

    def __init__(
        self,
        hkx_type: HKXType,
        absolute_offset=0,
        node_count=0,
        is_ptr=False,
        nodes=None,
        data_type=None,
        simple_array_flags: TagDataType = None,
    ):
        self.hkx_type = hkx_type
        self.absolute_offset = absolute_offset
        self.node_count = node_count
        self.is_ptr = is_ptr
        self.node_value = nodes
        self.data_type = data_type
        self.simple_array_flags = simple_array_flags  # optional `tag_type_flags` of simple array element type

    def __repr__(self):
        return (
            f"HKXItem:\n"
            f"        type = {self.hkx_type.name}\n"
            f"      offset = {self.absolute_offset}\n"
            f"  node_count = {self.node_count}\n"
            f"      is_ptr = {self.is_ptr}\n"
            f"       value = {self.node_value}\n"
            f"   data_type = {self.data_type.name if self.data_type else None}"
        )
