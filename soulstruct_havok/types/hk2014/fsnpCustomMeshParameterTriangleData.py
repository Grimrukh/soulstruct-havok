from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class fsnpCustomMeshParameterTriangleData(hk):
    alignment = 16
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3419166696

    local_members = (
        Member(0, "primitiveDataIndex", hkUint32),
        Member(4, "vertexDataIndex", hkUint32),
        Member(8, "vertexIndexA", hkUint32),
        Member(12, "vertexIndexB", hkUint32),
        Member(16, "vertexIndexC", hkUint32),
    )
    members = local_members

    primitiveDataIndex: int
    vertexDataIndex: int
    vertexIndexA: int
    vertexIndexB: int
    vertexIndexC: int
