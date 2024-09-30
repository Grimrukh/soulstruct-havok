from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hkxVertexBuffer import hkxVertexBuffer
from .hkxIndexBuffer import hkxIndexBuffer
from .hkxMaterial import hkxMaterial
from .hkxVertexAnimation import hkxVertexAnimation

from ..hkMeshBoneIndexMapping import hkMeshBoneIndexMapping


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMeshSection(hkReferencedObject):
    alignment = 8
    byte_size = 120
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member(24, "vertexBuffer", hkRefPtr(hkxVertexBuffer)),
        Member(32, "indexBuffers", hkArray(hkRefPtr(hkxIndexBuffer))),
        Member(48, "material", hkRefPtr(hkxMaterial)),
        Member(56, "userChannels", hkArray(hkRefVariant(hkReferencedObject, hsh=340571500))),
        Member(72, "vertexAnimations", hkArray(hkRefPtr(hkxVertexAnimation))),
        Member(88, "linearKeyFrameHints", hkArray(_float)),
        Member(104, "boneMatrixMap", hkArray(hkMeshBoneIndexMapping)),
    )
    members = hkReferencedObject.members + local_members

    vertexBuffer: hkxVertexBuffer
    indexBuffers: list[hkxIndexBuffer]
    material: hkxMaterial
    userChannels: list[hkReferencedObject]
    vertexAnimations: list[hkxVertexAnimation]
    linearKeyFrameHints: list[float]
    boneMatrixMap: list[hkMeshBoneIndexMapping]
