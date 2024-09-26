from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from soulstruct_havok.types.hk550.hkLocalFrame import hkLocalFrame


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeletonLocalFrameOnBone(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "localFrame", Ptr(hkLocalFrame)),
        Member(4, "boneIndex", hkInt32),
    )
    members = local_members

    localFrame: hkLocalFrame
    boneIndex: int
