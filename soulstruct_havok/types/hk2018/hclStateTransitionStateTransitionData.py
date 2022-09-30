from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hclStateTransitionSimClothTransitionData import hclStateTransitionSimClothTransitionData
from .hclStateTransitionBlendOpTransitionData import hclStateTransitionBlendOpTransitionData



class hclStateTransitionStateTransitionData(hk):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclStateTransition::StateTransitionData"

    local_members = (
        Member(0, "simClothTransitionData", hkArray(hclStateTransitionSimClothTransitionData)),
        Member(16, "blendOpTransitionData", hkArray(hclStateTransitionBlendOpTransitionData)),
        Member(32, "simulatedState", hkBool),
        Member(33, "emptyState", hkBool),
    )
    members = local_members

    simClothTransitionData: list[hclStateTransitionSimClothTransitionData]
    blendOpTransitionData: list[hclStateTransitionBlendOpTransitionData]
    simulatedState: bool
    emptyState: bool