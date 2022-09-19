from __future__ import annotations

from soulstruct_havok.enums import *
from .hkpShape import hkpShape


class hkpSphereRepShape(hkpShape):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()
