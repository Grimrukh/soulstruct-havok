from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkLocalFrame import hkLocalFrame


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeletonLocalFrameOnBone(hk):
    alignment = 16
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "localFrame", Ptr(hkLocalFrame)),
        Member(8, "boneIndex", hkInt16),
    )
    members = local_members

    localFrame: hkLocalFrame
    boneIndex: int
