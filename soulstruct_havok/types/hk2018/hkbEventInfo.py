from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbEventInfo(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3930708470

    local_members = (
        Member(0, "flags", hkFlags(hkUint32)),
    )
    members = local_members

    flags: hkUint32
