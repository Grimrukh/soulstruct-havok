from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpConvexPolytopeShapeConnectivityEdge(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hknpConvexPolytopeShape::Connectivity::Edge"

    local_members = (
        Member(0, "faceIndex", hkUint16),
        Member(2, "edgeIndex", hkUint8),
        Member(3, "padding", hkGenericStruct(hkUint8, 1), MemberFlags.NotSerializable),
    )
    members = local_members

    faceIndex: int
    edgeIndex: int
    padding: tuple[hkUint8]
