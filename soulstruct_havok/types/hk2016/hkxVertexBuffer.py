from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkxVertexBufferVertexData import hkxVertexBufferVertexData
from .hkxVertexDescription import hkxVertexDescription


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxVertexBuffer(hkReferencedObject):
    alignment = 8
    byte_size = 136
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(16, "data", hkxVertexBufferVertexData, MemberFlags.Protected),
        Member(120, "desc", hkxVertexDescription, MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    data: hkxVertexBufferVertexData
    desc: hkxVertexDescription
