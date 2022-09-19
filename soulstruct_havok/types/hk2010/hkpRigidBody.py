from __future__ import annotations

from soulstruct_havok.enums import *
from .hkpEntity import hkpEntity


class hkpRigidBody(hkpEntity):
    alignment = 16
    byte_size = 544
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1979242501
    local_members = ()
