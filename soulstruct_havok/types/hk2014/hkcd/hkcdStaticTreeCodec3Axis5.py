from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from ..core import *

from .hkcdStaticTreeCodec3Axis import hkcdStaticTreeCodec3Axis


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeCodec3Axis5(hkcdStaticTreeCodec3Axis):
    alignment = 2
    byte_size = 5
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkcdStaticTree::Codec3Axis5"
    __hsh = 316044371

    local_members = (
        Member(3, "hiData", hkUint8),
        Member(4, "loData", hkUint8),
    )
    members = hkcdStaticTreeCodec3Axis.members + local_members

    hiData: int
    loData: int

    @classmethod
    def unpack_primitive_array(cls, reader, length: int, offset: int = None) -> np.ndarray:
        """We can combine `xyz` and both data attributes into a 4-column `uint8` array."""
        data = reader.unpack(f"{length * 5}B")
        return np.array(data, dtype=np.uint8).reshape((length, 5))

    @classmethod
    def try_pack_primitive_array(cls, writer, value: list | np.ndarray) -> bool:
        """We can combine `xyz` and both data attributes into a 5-column `uint8` array."""
        if isinstance(value, list):
            value = np.array(value, dtype=np.uint8)
        if not isinstance(value, np.ndarray) or value.ndim != 2 or value.shape[1] != 5:
            return False
        writer.pack(f"{value.size}B", *value.flat)
        return True
