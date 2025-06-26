from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkpExtendedMeshShapeSubpart import hkpExtendedMeshShapeSubpart
from .hkpConvexShape import hkpConvexShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpExtendedMeshShapeShapesSubpart(hkpExtendedMeshShapeSubpart):
    alignment = 16
    byte_size = 152
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __real_name = "hkpExtendedMeshShape::ShapesSubpart"

    local_members = (
        Member(32, "childShapes", hkArray(hkRefPtr(hkpConvexShape))),
        Member(44, "numChildShapes", _int),
        Member(48, "offsetSet", hkBool),
        Member(52, "rotationSet", hkBool),
        Member(56, "transform", hkTransform),
        Member(120, "pad", hkStruct(_int, 8)),

    )
    members = hkpExtendedMeshShapeSubpart.members + local_members

    childShapes: list[hkpConvexShape]
    numChildShapes: int
    offsetSet: bool
    rotationSet: bool
    transform: hkTransform
    pad: tuple[int, ...]
