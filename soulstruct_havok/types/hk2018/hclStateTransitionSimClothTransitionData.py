from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hkHandle import hkHandle


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclStateTransitionSimClothTransitionData(hk):
    alignment = 8
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclStateTransition::SimClothTransitionData"

    local_members = (
        Member(0, "isSimulated", hkBool),
        Member(8, "transitionConstraints", hkArray(hkHandle)),
        Member(24, "transitionType", hkUint32),
    )
    members = local_members

    isSimulated: bool
    transitionConstraints: list[hkHandle]
    transitionType: int
