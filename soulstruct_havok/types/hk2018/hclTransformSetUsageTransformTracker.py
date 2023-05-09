from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkBitField import hkBitField


@dataclass(slots=True, eq=False, repr=False)
class hclTransformSetUsageTransformTracker(hk):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3022173165
    __real_name = "hclTransformSetUsage::TransformTracker"

    local_members = (
        Member(0, "read", hkBitField),
        Member(24, "readBeforeWrite", hkBitField),
        Member(48, "written", hkBitField),
    )
    members = local_members

    read: hkBitField
    readBeforeWrite: hkBitField
    written: hkBitField
