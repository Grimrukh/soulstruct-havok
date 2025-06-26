from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .._hkx.hkxMesh import hkxMesh
from .hkaSkeleton import hkaSkeleton
from .hkaMeshBindingMapping import hkaMeshBindingMapping


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaMeshBinding(hkReferencedObject):
    alignment = 16
    byte_size = 44
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "mesh", Ptr(hkxMesh)),
        Member(12, "originalSkeletonName", hkStringPtr),
        Member(16, "skeleton", Ptr(hkaSkeleton)),
        Member(20, "mappings", hkArray(hkaMeshBindingMapping)),
        Member(32, "boneFromSkinMeshTransforms", hkArray(hkTransform)),
    )
    members = hkReferencedObject.members + local_members

    mesh: hkxMesh
    originalSkeletonName: str
    skeleton: hkaSkeleton
    mappings: list[hkaMeshBindingMapping]
    boneFromSkinMeshTransforms: list[hkTransform]
