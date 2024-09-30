from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpBodyQuality(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "priority", hkInt32),
        Member(4, "supportedFlags", hkFlags(hkUint32)),
        Member(8, "requestedFlags", hkFlags(hkUint32)),
        Member(12, "contactCachingRelativeMovementThreshold", hkReal),
    )
    members = local_members

    priority: int
    supportedFlags: int
    requestedFlags: int
    contactCachingRelativeMovementThreshold: float
