from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkpStorageExtendedMeshShapeMaterial import hkpStorageExtendedMeshShapeMaterial
from .hkpNamedMeshMaterial import hkpNamedMeshMaterial


class hkpStorageExtendedMeshShapeMeshSubpartStorage(hkReferencedObject):
    alignment = 8
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1824184153
    __version = 3
    __real_name = "hkpStorageExtendedMeshShape::MeshSubpartStorage"

    local_members = (
        Member(16, "vertices", hkArray(hkVector4, hsh=2234779563)),
        Member(32, "indices8", hkArray(hkUint8, hsh=2877151166)),
        Member(48, "indices16", hkArray(hkUint16, hsh=3551656838)),
        Member(64, "indices32", hkArray(hkUint32)),
        Member(80, "materialIndices", hkArray(hkUint8, hsh=2877151166)),
        Member(96, "materials", hkArray(hkpStorageExtendedMeshShapeMaterial)),
        Member(112, "namedMaterials", hkArray(hkpNamedMeshMaterial)),
        Member(128, "materialIndices16", hkArray(hkUint16, hsh=3551656838)),
    )
    members = hkReferencedObject.members + local_members

    vertices: list[hkVector4]
    indices8: list[int]
    indices16: list[int]
    indices32: list[int]
    materialIndices: list[int]
    materials: list[hkpStorageExtendedMeshShapeMaterial]
    namedMaterials: list[hkpNamedMeshMaterial]
    materialIndices16: list[int]
