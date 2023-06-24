from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkpConvexShape import hkpConvexShape
from .hkpConvexVerticesConnectivity import hkpConvexVerticesConnectivity


@dataclass(slots=True, eq=False, repr=False)
class hkpConvexVerticesShape(hkpConvexShape):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1262392652
    __version = 6

    local_members = (
        Member(48, "aabbHalfExtents", hkVector4),
        Member(64, "aabbCenter", hkVector4),
        Member(80, "rotatedVertices", hkArray(hkMatrix3f, hsh=3015016790)),
        Member(96, "numVertices", hkInt32),
        Member(100, "useSpuBuffer", hkBool, MemberFlags.NotSerializable),
        Member(104, "planeEquations", hkArray(hkVector4, hsh=2234779563)),
        Member(120, "connectivity", Ptr(hkpConvexVerticesConnectivity, hsh=3931382236)),
    )
    members = hkpConvexShape.members + local_members

    aabbHalfExtents: Vector4
    aabbCenter: Vector4
    rotatedVertices: list[hkMatrix3f]
    numVertices: int
    useSpuBuffer: bool
    planeEquations: list[Vector4]
    connectivity: hkpConvexVerticesConnectivity
