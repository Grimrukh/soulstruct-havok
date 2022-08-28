from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkLocalFrame import hkLocalFrame


class hkaSkeletonLocalFrameOnBone(hk):
    alignment = 8
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkaSkeleton::LocalFrameOnBone"

    local_members = (
        Member(0, "localFrame", hkRefPtr(hkLocalFrame)),
        Member(8, "boneIndex", hkInt16),
    )
    members = local_members

    localFrame: hkLocalFrame
    boneIndex: int