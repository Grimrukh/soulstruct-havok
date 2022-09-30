from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hkxVertexBuffer import hkxVertexBuffer
from .hkxVertexAnimationUsageMap import hkxVertexAnimationUsageMap


class hkxVertexAnimation(hkReferencedObject):
    alignment = 8
    byte_size = 208
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 0

    local_members = (
        Member(24, "time", hkReal),
        Member(32, "vertData", hkxVertexBuffer),
        Member(176, "vertexIndexMap", hkArray(hkInt32)),
        Member(192, "componentMap", hkArray(hkxVertexAnimationUsageMap)),
    )
    members = hkReferencedObject.members + local_members

    time: float
    vertData: hkxVertexBuffer
    vertexIndexMap: list[int]
    componentMap: list[hkxVertexAnimationUsageMap]