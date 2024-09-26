from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from ..hkMoppBvTreeShapeBase import hkMoppBvTreeShapeBase
from .hkpSingleShapeContainer import hkpSingleShapeContainer


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpMoppBvTreeShape(hkMoppBvTreeShapeBase):
    alignment = 16
    byte_size = 64  # TODO: confirmed
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    # TODO: adjusted
    local_members = (
        Member(48, "child", hkpSingleShapeContainer, MemberFlags.Protected),
        Member(56, "childSize", _int, MemberFlags.NotSerializable),
        # missing member here?
    )

    members = hkMoppBvTreeShapeBase.members + local_members

    child: hkpSingleShapeContainer
    childSize: int
