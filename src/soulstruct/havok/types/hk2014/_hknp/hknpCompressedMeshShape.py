from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from ..hkBitField import hkBitField
from .hknpCompressedMeshShapeData import hknpCompressedMeshShapeData
from .hknpCompositeShape import hknpCompositeShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpCompressedMeshShape(hknpCompositeShape):
    alignment = 16
    byte_size = 160
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1600181558

    local_members = (
        Member(96, "data", Ptr(hknpCompressedMeshShapeData)),
        Member(104, "quadIsFlat", hkBitField),
        Member(128, "triangleIsInterior", hkBitField),
        # Eight pad bytes here.
    )
    members = hknpCompositeShape.members + local_members

    data: hknpCompressedMeshShapeData
    quadIsFlat: hkBitField
    triangleIsInterior: hkBitField
