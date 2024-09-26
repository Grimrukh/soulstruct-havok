from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpStorageExtendedMeshShapeMeshSubpartStorage(hkReferencedObject):
    alignment = 8
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpStorageExtendedMeshShape::MeshSubpartStorage"

    local_members = (
        Member(8, "vertices", hkArray(hkVector4, flags=0xC0000000)),
        Member(20, "indices16", hkArray(hkUint16, flags=0xC0000000)),  # note lack of `indices8`
        Member(32, "indices32", hkArray(hkUint32, flags=0xC0000000)),
        Member(44, "materialIndices", hkArray(hkUint8, flags=0xC0000000)),
        Member(56, "materials", hkArray(hkUint32, flags=0xC0000000)),
        Member(68, "materialIndices16", hkArray(hkUint16, flags=0xC0000000)),
    )
    members = hkReferencedObject.members + local_members

    vertices: np.ndarray  # `(n, 4)` float32 array
    indices16: list[int]
    indices32: list[int]
    materialIndices: list[int]
    materials: list[int]
    materialIndices16: list[int]
