from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from soulstruct_havok.enums import *
from .core import *

from .hkpStorageExtendedMeshShapeMaterial import hkpStorageExtendedMeshShapeMaterial
from .hkpNamedMeshMaterial import hkpNamedMeshMaterial


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpStorageExtendedMeshShapeMeshSubpartStorage(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpStorageExtendedMeshShape::MeshSubpartStorage"

    # TODO: adjusted
    local_members = (
        Member(8, "vertices", hkArray(hkVector4)),
        Member(20, "indices8", hkArray(hkUint8)),
        Member(32, "indices16", hkArray(hkUint16)),
        Member(44, "indices32", hkArray(hkUint32)),
        Member(56, "materialIndices", hkArray(hkUint8)),
        Member(68, "materials", hkArray(hkpStorageExtendedMeshShapeMaterial)),
        Member(80, "namedMaterials", hkArray(hkpNamedMeshMaterial)),
        Member(92, "materialIndices16", hkArray(hkUint16)),
    )
    members = hkReferencedObject.members + local_members

    vertices: np.ndarray  # `(n, 4)` float32 array
    indices8: list[int]
    indices16: list[int]
    indices32: list[int]
    materialIndices: list[int]
    materials: list[hkpStorageExtendedMeshShapeMaterial]
    namedMaterials: list[hkpNamedMeshMaterial]
    materialIndices16: list[int]
