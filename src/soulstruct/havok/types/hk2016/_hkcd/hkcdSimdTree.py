from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkcdSimdTreeNode import hkcdSimdTreeNode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdSimdTree(hkBaseObject):
    alignment = 4
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(8, "nodes", hkArray(hkcdSimdTreeNode)),
    )
    members = hkBaseObject.members + local_members

    nodes: list[hkcdSimdTreeNode]
