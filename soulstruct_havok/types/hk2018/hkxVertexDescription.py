from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxVertexDescriptionElementDecl import hkxVertexDescriptionElementDecl


@dataclass(slots=True, eq=False, repr=False)
class hkxVertexDescription(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "decls", hkArray(hkxVertexDescriptionElementDecl)),
    )
    members = local_members

    decls: list[hkxVertexDescriptionElementDecl]
