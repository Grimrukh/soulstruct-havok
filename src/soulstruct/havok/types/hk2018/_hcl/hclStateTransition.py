from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hclStateTransitionStateTransitionData import hclStateTransitionStateTransitionData
from ..hkHandle import hkHandle


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclStateTransition(hkReferencedObject):
    alignment = 8
    byte_size = 80
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "stateIds", hkArray(hkUint32, hsh=1109639201)),
        Member(48, "stateTransitionData", hkArray(hclStateTransitionStateTransitionData)),
        Member(64, "simClothTransitionConstraints", hkArray(hkArray(hkHandle))),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    stateIds: list[int]
    stateTransitionData: list[hclStateTransitionStateTransitionData]
    simClothTransitionConstraints: list[list[hkHandle]]
