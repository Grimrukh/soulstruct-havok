from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

from .hclStateTransitionTransitionType import hclStateTransitionTransitionType
from .hclBlendSomeVerticesOperatorBlendWeightType import hclBlendSomeVerticesOperatorBlendWeightType


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclStateTransitionBlendOpTransitionData(hk):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclStateTransition::BlendOpTransitionData"

    local_members = (
        Member(0, "bufferASimCloths", hkArray(_int, hsh=910429161)),
        Member(16, "bufferBSimCloths", hkArray(_int, hsh=910429161)),
        Member(32, "transitionType", hkEnum(hclStateTransitionTransitionType, hkUint32)),
        Member(36, "blendWeightType", hclBlendSomeVerticesOperatorBlendWeightType),
        Member(40, "blendOperatorId", _unsigned_int),
    )
    members = local_members

    bufferASimCloths: list[int]
    bufferBSimCloths: list[int]
    transitionType: hclStateTransitionTransitionType
    blendWeightType: int
    blendOperatorId: int
