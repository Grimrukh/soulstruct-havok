from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxNodeAnnotationData(hk):
    alignment = 4
    byte_size = 8
    tag_type_flags = TagDataType.Class
    __real_name = "hkxNode::AnnotationData"

    __tag_format_flags = 41
    __hsh = 1377735959

    local_members = (
        Member(0, "time", hkReal),
        Member(4, "description", hkStringPtr),
    )
    members = local_members

    time: float
    descriptiopn: str
