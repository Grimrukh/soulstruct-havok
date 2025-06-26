from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from .core import *
from .fsnpCustomMeshParameterPrimitiveData import fsnpCustomMeshParameterPrimitiveData
from .fsnpCustomMeshParameterTriangleData import fsnpCustomMeshParameterTriangleData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class fsnpCustomMeshParameter(hkReferencedObject):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3608770766

    local_members = (
        Member(16, "triangleDataArray", hkArray(hkUint8)),
        Member(32, "primitiveDataArray", hkArray(hkUint8)),
        Member(48, "vertexDataStride", hkInt32),
        Member(52, "triangleDataStride", hkInt32),
        Member(56, "version", hkUint32),
        Member(60, "unk", hkUint32),  # TODO: not a real member
    )
    members = hkReferencedObject.members + local_members

    triangleDataArray: list[fsnpCustomMeshParameterTriangleData]
    primitiveDataArray: list[fsnpCustomMeshParameterPrimitiveData]
    vertexDataStride: int
    triangleDataStride: int
    version: int
    unk: int = 0
