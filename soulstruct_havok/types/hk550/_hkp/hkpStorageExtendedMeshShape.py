from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkpExtendedMeshShape import hkpExtendedMeshShape
from .hkpStorageExtendedMeshShapeMeshSubpartStorage import hkpStorageExtendedMeshShapeMeshSubpartStorage
from .hkpStorageExtendedMeshShapeShapeSubpartStorage import hkpStorageExtendedMeshShapeShapeSubpartStorage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpStorageExtendedMeshShape(hkpExtendedMeshShape):
    alignment = 16
    byte_size = 216
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        # TODO: confirmed
        Member(
            192,
            "meshstorage",
            hkArray(Ptr(hkpStorageExtendedMeshShapeMeshSubpartStorage), flags=0xC0000000),
            MemberFlags.Protected,
        ),
        Member(
            204,  # empty
            "shapestorage",
            hkArray(Ptr(hkpStorageExtendedMeshShapeShapeSubpartStorage), flags=0xC0000000),
            MemberFlags.Protected,
        ),
    )
    members = hkpExtendedMeshShape.members + local_members

    meshstorage: list[hkpStorageExtendedMeshShapeMeshSubpartStorage]
    shapestorage: list[hkpStorageExtendedMeshShapeShapeSubpartStorage]
