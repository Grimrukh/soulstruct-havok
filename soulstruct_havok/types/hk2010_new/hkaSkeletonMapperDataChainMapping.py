from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


class hkaSkeletonMapperDataChainMapping(hk):
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "startBoneA", hkInt16),
        Member(2, "endBoneA", hkInt16),
        Member(4, "startBoneB", hkInt16),
        Member(6, "endBoneB", hkInt16),
        Member(16, "startAFromBTransform", hkQsTransform),
        Member(64, "endAFromBTransform", hkQsTransform),
    )
    members = local_members

    startBoneA: int
    endBoneA: int
    startBoneB: int
    endBoneB: int
    startAFromBTransform: hkQsTransform
    endAFromBTransform: hkQsTransform
