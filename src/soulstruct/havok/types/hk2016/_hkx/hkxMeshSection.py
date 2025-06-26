from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxVertexBuffer import hkxVertexBuffer
from .hkxIndexBuffer import hkxIndexBuffer
from .hkxMaterial import hkxMaterial
from .hkxVertexAnimation import hkxVertexAnimation
from ..hkMeshBoneIndexMapping import hkMeshBoneIndexMapping


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMeshSection(hkReferencedObject):
    alignment = 8
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member(16, "vertexBuffer", hkRefPtr(hkxVertexBuffer)),
        Member(24, "indexBuffers", hkArray(hkRefPtr(hkxIndexBuffer))),
        Member(40, "material", hkRefPtr(hkxMaterial)),
        Member(48, "userChannels", hkArray(hkRefVariant(hkReferencedObject, hsh=2872857893))),
        Member(64, "vertexAnimations", hkArray(hkRefPtr(hkxVertexAnimation))),
        Member(80, "linearKeyFrameHints", hkArray(_float)),
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
