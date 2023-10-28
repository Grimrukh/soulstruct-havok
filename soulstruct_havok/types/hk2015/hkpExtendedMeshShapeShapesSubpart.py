from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkpExtendedMeshShapeSubpart import hkpExtendedMeshShapeSubpart
from .hkpConvexShape import hkpConvexShape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpExtendedMeshShapeShapesSubpart(hkpExtendedMeshShapeSubpart):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1
    __real_name = "hkpExtendedMeshShape::ShapesSubpart"

    local_members = (
        Member(32, "childShapes", hkArray(hkRefPtr(hkpConvexShape))),
        Member(48, "rotation", hkQuaternion, MemberFlags.Protected),
        Member(64, "translation", hkVector4, MemberFlags.Protected),
    )
    members = hkpExtendedMeshShapeSubpart.members + local_members

    childShapes: list[hkpConvexShape]
    rotation: hkQuaternion
    translation: Vector4
