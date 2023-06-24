from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkMoppBvTreeShapeBase import hkMoppBvTreeShapeBase
from .hkpSingleShapeContainer import hkpSingleShapeContainer


@dataclass(slots=True, eq=False, repr=False)
class hkpMoppBvTreeShape(hkMoppBvTreeShapeBase):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2039906177

    local_members = (
        Member(80, "child", hkpSingleShapeContainer, MemberFlags.Protected),
        Member(96, "childSize", _int, MemberFlags.NotSerializable),
    )
    members = hkMoppBvTreeShapeBase.members + local_members

    child: hkpSingleShapeContainer
    childSize: int
