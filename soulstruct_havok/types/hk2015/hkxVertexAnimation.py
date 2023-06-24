from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkxVertexBuffer import hkxVertexBuffer
from .hkxVertexAnimationUsageMap import hkxVertexAnimationUsageMap


@dataclass(slots=True, eq=False, repr=False)
class hkxVertexAnimation(hkReferencedObject):
    alignment = 8
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 0

    local_members = (
        Member(16, "time", hkReal),
        Member(24, "vertData", hkxVertexBuffer),
        Member(160, "vertexIndexMap", hkArray(hkInt32)),
        Member(176, "componentMap", hkArray(hkxVertexAnimationUsageMap)),
    )
    members = hkReferencedObject.members + local_members

    time: float
    vertData: hkxVertexBuffer
    vertexIndexMap: list[int]
    componentMap: list[hkxVertexAnimationUsageMap]
