from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hclBufferLayoutSlotFlags import hclBufferLayoutSlotFlags


@dataclass(slots=True, eq=False, repr=False)
class hclBufferLayoutSlot(hk):
    alignment = 1
    byte_size = 2
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclBufferLayout::Slot"

    local_members = (
        Member(0, "flags", hkEnum(hclBufferLayoutSlotFlags, hkUint8)),
        Member(1, "stride", hkUint8),
    )
    members = local_members

    flags: hclBufferLayoutSlotFlags
    stride: int
