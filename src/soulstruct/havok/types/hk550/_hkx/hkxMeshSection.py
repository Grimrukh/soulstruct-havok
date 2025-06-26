from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxVertexBuffer import hkxVertexBuffer
from .hkxIndexBuffer import hkxIndexBuffer
from .hkxMaterial import hkxMaterial


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMeshSection(hk):
    alignment = 4
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2435614819

    local_members = (
        Member(0, "vertexBuffer", Ptr(hkxVertexBuffer)),
        Member(4, "indexBuffers", SimpleArray(Ptr(hkxIndexBuffer))),
        Member(12, "material", Ptr(hkxMaterial)),
        Member(16, "userChannels", SimpleArray(Ptr(hkReferencedObject))),  # `hkVariant.m_class`
    )
    members = local_members

    vertexBuffer: hkxVertexBuffer
    indexBuffers: list[hkxIndexBuffer]
    material: hkxMaterial
    userChannels: list[hkReferencedObject]
