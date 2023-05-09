from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hknpPhysicsSystemData import hknpPhysicsSystemData
from .hkaSkeleton import hkaSkeleton


@dataclass(slots=True, eq=False, repr=False)
class hknpRagdollData(hknpPhysicsSystemData):
    alignment = 16
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3700367531

    local_members = (
        Member(120, "skeleton", Ptr(hkaSkeleton)),
        Member(128, "boneToBodyMap", hkArray(hkInt32)),
    )
    members = hknpPhysicsSystemData.members + local_members

    skeleton: hkaSkeleton
    boneToBodyMap: list[int]
