from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hknp.hknpCompressedMeshShape import hknpCompressedMeshShape
from .fsnpCustomMeshParameter import fsnpCustomMeshParameter


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class fsnpCustomParamCompressedMeshShape(hknpCompressedMeshShape):
    alignment = 16
    byte_size = 184
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3608770766

    local_members = (
        Member(160, "pParam", Ptr(fsnpCustomMeshParameter)),
        Member(168, "triangleIndexToShapeKey", hkArray(hkUint32)),
        # Eight byte pad here.
    )
    members = hknpCompressedMeshShape.members + local_members

    pParam: fsnpCustomMeshParameter
    triangleIndexToShapeKey: list[int]
