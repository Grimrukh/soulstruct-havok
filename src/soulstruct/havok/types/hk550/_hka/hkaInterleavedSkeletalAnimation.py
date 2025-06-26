from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaSkeletalAnimation import hkaSkeletalAnimation


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaInterleavedSkeletalAnimation(hkaSkeletalAnimation):
    alignment = 4
    byte_size = 52
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1655713403

    local_members = (
        Member(36, "transforms", SimpleArray(hkQsTransform)),
        Member(44, "floats", SimpleArray(hkReal)),
    )
    members = hkaSkeletalAnimation.members + local_members

    transforms: list[hkQsTransform]
    floats: list[float]
