from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbBindable import hkbBindable


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbBoneIndexArray(hkbBindable):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3464013926

    local_members = (
        Member(56, "boneIndices", hkArray(hkInt16, hsh=3571075457)),
    )
    members = hkbBindable.members + local_members

    boneIndices: list[int]
