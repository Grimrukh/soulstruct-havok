from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct.havok.enums import *
from .core import *

from .hkGeometryTriangle import hkGeometryTriangle


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkGeometry(hkReferencedObject):
    alignment = 4
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "vertices", hkArray(hkVector4)),
        Member(12, "triangles", hkArray(hkGeometryTriangle)),
    )
    members = hkReferencedObject.members + local_members

    vertices: np.ndarray  # `(n, 4)` float32 array
    triangles: list[hkGeometryTriangle]
