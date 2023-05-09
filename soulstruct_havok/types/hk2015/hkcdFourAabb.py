from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkcdFourAabb(hk):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "lx", hkVector4),
        Member(16, "hx", hkVector4),
        Member(32, "ly", hkVector4),
        Member(48, "hy", hkVector4),
        Member(64, "lz", hkVector4),
        Member(80, "hz", hkVector4),
    )
    members = local_members

    lx: hkVector4
    hx: hkVector4
    ly: hkVector4
    hy: hkVector4
    lz: hkVector4
    hz: hkVector4
