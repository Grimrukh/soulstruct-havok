from __future__ import annotations

from soulstruct_havok.enums import *
from .hkBitFieldBase import hkBitFieldBase


class hkBitField(hkBitFieldBase):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2
    local_members = ()
