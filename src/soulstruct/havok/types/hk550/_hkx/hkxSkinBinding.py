from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkxMesh import hkxMesh
from .hkxNode import hkxNode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxSkinBinding(hk):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3308439312

    local_members = (
        Member(0, "mesh", Ptr(hkxMesh)),
        Member(4, "mapping", SimpleArray(hkxNode)),
        Member(12, "bindPose", SimpleArray(hkMatrix4)),
        Member(32, "initSkinTransform", hkMatrix4),
    )
    members = local_members

    mesh: hkxMesh
    mapping: list[hkxNode]
    bindPose: list[hkMatrix4]
    initSkinTransform: hkMatrix4
