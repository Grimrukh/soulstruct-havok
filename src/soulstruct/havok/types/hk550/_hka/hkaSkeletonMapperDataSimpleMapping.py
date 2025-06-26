from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaSkeletonMapperDataSimpleMapping(hk):
    alignment = 16
    byte_size = 64
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "boneA", hkInt16),
        Member(2, "boneB", hkInt16),
        Member(16, "aFromBTransform", hkQsTransform),
    )
    members = local_members

    boneA: int
    boneB: int
    aFromBTransform: hkQsTransform
