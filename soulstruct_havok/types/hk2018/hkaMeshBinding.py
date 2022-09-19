from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *

from .hkxMesh import hkxMesh

from .hkaSkeleton import hkaSkeleton
from .hkaMeshBindingMapping import hkaMeshBindingMapping



class hkaMeshBinding(hkReferencedObject):
    alignment = 8
    byte_size = 88
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 3

    local_members = (
        Member(24, "mesh", hkRefPtr(hkxMesh)),
        Member(32, "originalSkeletonName", hkStringPtr),
        Member(40, "name", hkStringPtr),
        Member(48, "skeleton", hkRefPtr(hkaSkeleton, hsh=3659816570)),
        Member(56, "mappings", hkArray(hkaMeshBindingMapping)),
        Member(72, "boneFromSkinMeshTransforms", hkArray(hkTransform)),
    )
    members = hkReferencedObject.members + local_members

    mesh: hkxMesh
    originalSkeletonName: hkStringPtr
    name: hkStringPtr
    skeleton: hkaSkeleton
    mappings: list[hkaMeshBindingMapping]
    boneFromSkinMeshTransforms: list[hkTransform]
