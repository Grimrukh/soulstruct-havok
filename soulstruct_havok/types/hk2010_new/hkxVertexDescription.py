from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxVertexDescriptionElementDecl import hkxVertexDescriptionElementDecl


class hkxVertexDescription(hk):
    alignment = 16
    byte_size = 12
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "decls", hkArray(hkxVertexDescriptionElementDecl)),
    )
    members = local_members

    decls: list[hkxVertexDescriptionElementDecl]
