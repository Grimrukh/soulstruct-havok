from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from .core import *

from .hknpShape import hknpShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpConvexShape(hknpShape):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(40, "vertices", hkRelArray(hkVector4)),
    )
    members = hknpShape.members + local_members

    vertices: np.ndarray  # `(n, 4)` float32 array
