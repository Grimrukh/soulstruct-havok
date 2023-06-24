from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkxVertexBuffer import hkxVertexBuffer
from .hkxIndexBuffer import hkxIndexBuffer
from .hkxMaterial import hkxMaterial
from .hkxVertexAnimation import hkxVertexAnimation
from .hkMeshBoneIndexMapping import hkMeshBoneIndexMapping


@dataclass(slots=True, eq=False, repr=False)
class hkxMeshSection(hkReferencedObject):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 5

    local_members = (
        Member(16, "vertexBuffer", Ptr(hkxVertexBuffer)),
        Member(24, "indexBuffers", hkArray(Ptr(hkxIndexBuffer))),
        Member(40, "material", Ptr(hkxMaterial)),
        Member(48, "userChannels", hkArray(Ptr(hkReferencedObject))),
        Member(64, "vertexAnimations", hkArray(Ptr(hkxVertexAnimation))),
        Member(80, "linearKeyFrameHints", hkArray(hkReal)),
        Member(96, "boneMatrixMap", hkArray(hkMeshBoneIndexMapping)),
    )
    members = hkReferencedObject.members + local_members

    vertexBuffer: hkxVertexBuffer
    indexBuffers: list[hkxIndexBuffer]
    material: hkxMaterial
    userChannels: list[hkReferencedObject]
    vertexAnimations: list[hkxVertexAnimation]
    linearKeyFrameHints: list[float]
    boneMatrixMap: list[hkMeshBoneIndexMapping]
