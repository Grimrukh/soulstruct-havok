from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkxVertexBufferVertexData import hkxVertexBufferVertexData
from .hkxVertexDescription import hkxVertexDescription


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxVertexBuffer(hkReferencedObject):
    alignment = 16
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "data", hkxVertexBufferVertexData),
        Member(92, "desc", hkxVertexDescription),
    )
    members = hkReferencedObject.members + local_members

    data: hkxVertexBufferVertexData
    desc: hkxVertexDescription
