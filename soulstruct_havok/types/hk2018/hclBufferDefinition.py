from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hclBufferLayout import hclBufferLayout


@dataclass(slots=True, eq=False, repr=False)
class hclBufferDefinition(hkReferencedObject):
    alignment = 8
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2503985032
    __version = 1

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "type", hkInt32),
        Member(36, "subType", hkInt32),
        Member(40, "numVertices", hkUint32),
        Member(44, "numTriangles", hkUint32),
        Member(48, "bufferLayout", hclBufferLayout),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    type: int
    subType: int
    numVertices: int
    numTriangles: int
    bufferLayout: hclBufferLayout
