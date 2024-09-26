from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimatedReferenceFramehkaReferenceFrameTypeEnum(hk):
    alignment = 1
    byte_size = 1
    tag_type_flags = TagDataType.Int | TagDataType.IsSigned | TagDataType.Int8
    __real_name = "hkaAnimatedReferenceFrame::hkaReferenceFrameTypeEnum"
    local_members = ()
