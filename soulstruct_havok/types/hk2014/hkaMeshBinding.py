from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkxMesh import hkxMesh
from .hkaSkeleton import hkaSkeleton
from .hkaMeshBindingMapping import hkaMeshBindingMapping


class hkaMeshBinding(hkReferencedObject):
    alignment = 16
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 3

    local_members = (
        Member(16, "mesh", Ptr(hkxMesh)),
        Member(24, "originalSkeletonName", hkStringPtr),
        Member(32, "name", hkStringPtr),
        Member(40, "skeleton", Ptr(hkaSkeleton)),
        Member(48, "mappings", hkArray(hkaMeshBindingMapping)),
        Member(64, "boneFromSkinMeshTransforms", hkArray(hkTransform)),
    )
    members = hkReferencedObject.members + local_members

    mesh: hkxMesh
    originalSkeletonName: str
    name: str
    skeleton: hkaSkeleton
    mappings: list[hkaMeshBindingMapping]
    boneFromSkinMeshTransforms: list[hkTransform]