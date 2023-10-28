from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkpConvexShape import hkpConvexShape
from .hkpSingleShapeContainer import hkpSingleShapeContainer


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpConvexTransformShapeBase(hkpConvexShape):
    alignment = 8
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(40, "childShape", hkpSingleShapeContainer, MemberFlags.Protected),
        Member(56, "childShapeSizeForSpu", _int, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = hkpConvexShape.members + local_members

    childShape: hkpSingleShapeContainer
    childShapeSizeForSpu: int
