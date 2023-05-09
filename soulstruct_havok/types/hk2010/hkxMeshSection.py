from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkxVertexBuffer import hkxVertexBuffer
from .hkxIndexBuffer import hkxIndexBuffer
from .hkxMaterial import hkxMaterial


@dataclass(slots=True, eq=False, repr=False)
class hkxMeshSection(hkReferencedObject):
    alignment = 16
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "vertexBuffer", Ptr(hkxVertexBuffer)),
        Member(12, "indexBuffers", hkArray(Ptr(hkxIndexBuffer))),
        Member(24, "material", Ptr(hkxMaterial)),
        Member(28, "userChannels", hkArray(Ptr(hkReferencedObject))),
    )
    members = hkReferencedObject.members + local_members

    vertexBuffer: hkxVertexBuffer
    indexBuffers: list[hkxIndexBuffer]
    material: hkxMaterial
    userChannels: list[hkReferencedObject]
