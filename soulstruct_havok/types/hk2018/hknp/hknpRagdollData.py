from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hknpPhysicsSystemData import hknpPhysicsSystemData
from ..hka.hkaSkeleton import hkaSkeleton


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpRagdollData(hknpPhysicsSystemData):
    alignment = 8
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3702196028
    __version = 1

    local_members = (
        Member(104, "skeleton", hkRefPtr(hkaSkeleton, hsh=3659816570)),
        Member(112, "boneToBodyMap", hkArray(_int, hsh=910429161)),
        Member(128, "bodyTags", hkArray(hkUint32)),
    )
    members = hknpPhysicsSystemData.members + local_members

    skeleton: hkaSkeleton
    boneToBodyMap: list[int]
    bodyTags: list[int]
