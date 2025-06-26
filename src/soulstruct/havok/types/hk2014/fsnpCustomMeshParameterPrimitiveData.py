from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class fsnpCustomMeshParameterPrimitiveData(hk):
    alignment = 16
    byte_size = 52
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3013233085

    local_members = (
        Member(0, "vertexData", hkArray(hkUint8)),
        Member(16, "triangleData", hkArray(hkUint8)),
        Member(32, "primitiveData", hkArray(hkUint8)),
        Member(48, "materialNameData", hkUint32),
    )
    members = local_members

    vertexData: list[int]
    triangleData: list[int]
    primitiveData: list[int]
    materialNameData: int
