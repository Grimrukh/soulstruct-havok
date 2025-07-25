from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from ..hkGeometry import hkGeometry
from .hknpExternMeshShapeGeometry import hknpExternMeshShapeGeometry


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpDefaultExternMeshShapeGeometry(hknpExternMeshShapeGeometry):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "geometry", hkRefPtr(hkGeometry)),
    )
    members = hknpExternMeshShapeGeometry.members + local_members

    geometry: hkGeometry
