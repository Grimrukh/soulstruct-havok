from __future__ import annotations

from soulstruct_havok.enums import *
from .hkpMotion import hkpMotion


class hkpKeyframedRigidMotion(hkpMotion):
    alignment = 16
    byte_size = 320
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()
