from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hkaSkeletonPartition(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 1

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "startBoneIndex", hkInt16),
        Member(10, "numBones", hkInt16),
    )
    members = local_members

    name: str
    startBoneIndex: int
    numBones: int
