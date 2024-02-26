from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbBindable import hkbBindable


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbBoneWeightArray(hkbBindable):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(56, "boneWeights", hkArray(hkReal)),
    )
    members = hkbBindable.members + local_members

    boneWeights: list[float]
