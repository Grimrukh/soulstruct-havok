from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *

from ..core import *
from .hkpMeshShape import hkpMeshShape
from .hkpStorageMeshShapeSubpartStorage import hkpStorageMeshShapeSubpartStorage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpStorageMeshShape(hkpMeshShape):
    alignment = 8
    byte_size = 108
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    local_members = (
        Member(96, "storage", hkArray(Ptr(hkpStorageMeshShapeSubpartStorage))),  # TODO: flags 0xC0000000?
    )

    members = hkpMeshShape.members + local_members

    storage: list[hkpStorageMeshShapeSubpartStorage]
