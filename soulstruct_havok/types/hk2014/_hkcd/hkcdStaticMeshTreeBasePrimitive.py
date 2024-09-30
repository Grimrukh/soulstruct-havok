from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticMeshTreeBasePrimitive(hk):
    """
    public enum Type
    {
        INVALID = 0,
        TRIANGLE = 1,
        QUAD = 2,
        CUSTOM = 3,
        NUM_TYPES = 4,
    }
    """
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1457139580

    local_members = (
        Member(0, "indices_0", hkUint8),
        Member(1, "indices_1", hkUint8),
        Member(2, "indices_2", hkUint8),
        Member(3, "indices_3", hkUint8),
    )
    members = local_members

    indices_0: int
    indices_1: int
    indices_2: int
    indices_3: int

    @classmethod
    def unpack_primitive_array(cls, reader, length: int, offset: int = None) -> np.ndarray:
        """An array of this class can be loaded as an `(n, 4)` uint8 array of indices."""
        fmt = f"{length * 4}B"
        data = reader.unpack(fmt, offset=offset)
        return np.array(data, dtype=np.uint8).reshape((-1, 4))

    @classmethod
    def try_pack_primitive_array(cls, writer: BinaryWriter, value: list | np.ndarray) -> bool:
        """Attempt to pack a `(n, 4)` uint8 array of indices."""
        if not isinstance(value, (list, np.ndarray)):
            return False
        if isinstance(value, list):
            value = np.array(value, dtype=np.uint8)
        if value.ndim != 2 or value.shape[1] != 4:
            return False
        writer.pack(f"{value.size}B", *value.flatten())
        return True
