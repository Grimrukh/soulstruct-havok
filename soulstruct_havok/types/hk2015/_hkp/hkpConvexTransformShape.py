from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hkpConvexTransformShapeBase import hkpConvexTransformShapeBase


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpConvexTransformShape(hkpConvexTransformShapeBase):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 992058212
    __version = 3

    local_members = (
        Member(64, "transform", hkQsTransform, MemberFlags.Protected),
        Member(112, "extraScale", hkVector4, MemberFlags.Protected),
    )
    members = hkpConvexTransformShapeBase.members + local_members

    transform: hkQsTransform
    extraScale: Vector4
