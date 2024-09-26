from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hknpShape import hknpShape
from .hknpSparseCompactMap import hknpSparseCompactMap


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpCompositeShape(hknpShape):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(48, "edgeWeldingMap", hknpSparseCompactMap, MemberFlags.Protected),
        Member(88, "shapeTagCodecInfo", hkUint32),
        # Four pad bytes here.
    )
    members = hknpShape.members + local_members

    edgeWeldingMap: hknpSparseCompactMap
    shapeTagCodecInfo: int
