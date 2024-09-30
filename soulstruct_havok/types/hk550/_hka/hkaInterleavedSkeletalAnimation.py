from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkaSkeletalAnimation import hkaSkeletalAnimation


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaInterleavedSkeletalAnimation(hkaSkeletalAnimation):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3449291259  # TODO

    local_members = (
        Member(36, "transforms", hkArray(hkQsTransform), MemberFlags.Private),
    )
    members = hkaSkeletalAnimation.members + local_members

    transforms: list[hkQsTransform]
