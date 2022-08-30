from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkcdSimdTreeNode import hkcdSimdTreeNode


class hkcdSimdTree(hkBaseObject):
    alignment = 4
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "nodes", hkArray(hkcdSimdTreeNode)),
    )
    members = hkBaseObject.members + local_members

    nodes: list[hkcdSimdTreeNode]
