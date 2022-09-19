from __future__ import annotations

from soulstruct_havok.enums import *
from .hkcdShape import hkcdShape


class hkpShapeBase(hkcdShape):
    alignment = 8
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()
