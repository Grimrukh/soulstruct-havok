from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


class hkpConvexListFilter(hkReferencedObject):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    local_members = ()
