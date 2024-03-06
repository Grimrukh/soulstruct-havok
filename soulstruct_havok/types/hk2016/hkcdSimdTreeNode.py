from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkcdFourAabb import hkcdFourAabb


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdSimdTreeNode(hkcdFourAabb):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkcdSimdTree::Node"

    local_members = (
        Member(96, "data", hkGenericStruct(hkUint32, 4)),
    )
    members = hkcdFourAabb.members + local_members

    data: tuple[hkUint32]
