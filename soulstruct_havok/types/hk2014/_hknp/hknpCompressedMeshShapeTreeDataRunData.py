from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpCompressedMeshShapeTreeDataRunData(hk):
    alignment = 2
    byte_size = 2
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3260246059

    local_members = (
        Member(0, "data", hkUint16),
    )
    members = local_members

    data: int

    @classmethod
    def unpack_primitive_array(cls, reader, length: int, offset: int = None) -> np.ndarray:
        """Can unpack `data` directly in to a `uint16` array."""
        data = reader.unpack(f"{length}H", offset=offset)
        return np.array(data, dtype=np.uint16)

    # Base primitive array pack is fine.
