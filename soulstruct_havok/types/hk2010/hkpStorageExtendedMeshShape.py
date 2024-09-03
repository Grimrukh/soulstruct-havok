from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpExtendedMeshShape import hkpExtendedMeshShape
from .hkpStorageExtendedMeshShapeMeshSubpartStorage import hkpStorageExtendedMeshShapeMeshSubpartStorage
from .hkpStorageExtendedMeshShapeShapeSubpartStorage import hkpStorageExtendedMeshShapeShapeSubpartStorage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpStorageExtendedMeshShape(hkpExtendedMeshShape):
    alignment = 16
    byte_size = 264
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    # TODO: adjusted
    local_members = (
        Member(
            240,
            "meshstorage",
            hkArray(Ptr(hkpStorageExtendedMeshShapeMeshSubpartStorage)),
            MemberFlags.Protected,
        ),
        Member(
            252,
            "shapestorage",
            hkArray(Ptr(hkpStorageExtendedMeshShapeShapeSubpartStorage)),
            MemberFlags.Protected,
        ),
    )
    members = hkpExtendedMeshShape.members + local_members

    meshstorage: list[hkpStorageExtendedMeshShapeMeshSubpartStorage]
    shapestorage: list[hkpStorageExtendedMeshShapeShapeSubpartStorage]
