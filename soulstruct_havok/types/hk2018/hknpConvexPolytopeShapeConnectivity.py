from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hknpConvexPolytopeShapeConnectivityEdge import hknpConvexPolytopeShapeConnectivityEdge


@dataclass(slots=True, eq=False, repr=False)
class hknpConvexPolytopeShapeConnectivity(hkReferencedObject):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hknpConvexPolytopeShape::Connectivity"

    local_members = (
        Member(24, "vertexEdges", hkArray(hknpConvexPolytopeShapeConnectivityEdge)),
        Member(40, "faceLinks", hkArray(hknpConvexPolytopeShapeConnectivityEdge)),
    )
    members = hkReferencedObject.members + local_members

    vertexEdges: list[hknpConvexPolytopeShapeConnectivityEdge]
    faceLinks: list[hknpConvexPolytopeShapeConnectivityEdge]
