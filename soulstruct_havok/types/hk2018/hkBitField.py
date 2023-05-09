from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkBitFieldBase import hkBitFieldBase


@dataclass(slots=True, eq=False, repr=False)
class hkBitField(hkBitFieldBase):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2
    local_members = ()
