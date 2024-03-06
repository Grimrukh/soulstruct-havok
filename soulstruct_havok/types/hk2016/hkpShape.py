from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkpShapeBase import hkpShapeBase


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpShape(hkpShapeBase):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(24, "userData", hkUlong),
    )
    members = hkpShapeBase.members + local_members

    userData: int
