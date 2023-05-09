from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *

from .hclBufferUsage import hclBufferUsage


@dataclass(slots=True, eq=False, repr=False)
class hclClothStateBufferAccess(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 746522671
    __version = 2
    __real_name = "hclClothState::BufferAccess"

    local_members = (
        Member(0, "bufferIndex", hkUint32),
        Member(4, "bufferUsage", hclBufferUsage),
        Member(12, "shadowBufferIndex", hkUint32),
    )
    members = local_members

    bufferIndex: int
    bufferUsage: hclBufferUsage
    shadowBufferIndex: int
