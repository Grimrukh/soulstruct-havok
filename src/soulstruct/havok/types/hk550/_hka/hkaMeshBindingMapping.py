from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaMeshBindingMapping(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1302767348

    local_members = (
        Member(0, "mapping", hkArray(hkInt16)),
    )
    members = local_members

    mapping: list[int]
