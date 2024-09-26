from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclSimClothPose(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3477682756

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "positions", hkArray(hkVector4, hsh=1398146255)),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    positions: np.ndarray  # `(n, 4)` float32 array
