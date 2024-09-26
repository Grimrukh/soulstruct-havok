from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from ..hkMoppBvTreeShapeBase import hkMoppBvTreeShapeBase
from .hkpSingleShapeContainer import hkpSingleShapeContainer


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpMoppBvTreeShape(hkMoppBvTreeShapeBase):
    alignment = 16
    byte_size = 60
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    # TODO: Base class seems to only have size 44, but these members start at 48,
    #  unless `hkpSingleShapeContainer`'s members start at 8 rather than 4.
    #  All serialized data is zero anyway; only the `child` member pointer really matters.
    local_members = (
        Member(48, "child", hkpSingleShapeContainer, MemberFlags.Protected),
        Member(56, "childSize", _int, MemberFlags.NotSerializable),
    )

    members = hkMoppBvTreeShapeBase.members + local_members

    child: hkpSingleShapeContainer
    childSize: int = 0
