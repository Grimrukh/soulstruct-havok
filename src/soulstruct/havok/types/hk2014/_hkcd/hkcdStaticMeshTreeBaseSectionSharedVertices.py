from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticMeshTreeBaseSectionSharedVertices(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 727890741

    local_members = (
        Member(0, "data", hkUint32),
    )
    members = local_members

    data: int

    @classmethod
    def unpack_primitive_array(cls, reader, length: int, offset: int = None) -> np.ndarray:
        """Can unpack `data` directly in to a `uint32` array."""
        data = reader.unpack(f"{length}I", offset=offset)
        return np.array(data, dtype=np.uint16)

    # Base primitive array pack is fine.
