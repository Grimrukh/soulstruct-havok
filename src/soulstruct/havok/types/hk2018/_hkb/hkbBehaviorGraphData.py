from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbVariableInfo import hkbVariableInfo
from .hkbEventInfo import hkbEventInfo
from .hkbVariableBounds import hkbVariableBounds
from .hkbVariableValueSet import hkbVariableValueSet
from .hkbBehaviorGraphStringData import hkbBehaviorGraphStringData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbBehaviorGraphData(hkReferencedObject):
    alignment = 8
    byte_size = 120
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 4234497696
    __version = 3

    local_members = (
        Member(24, "attributeDefaults", hkArray(hkReal)),
        Member(40, "variableInfos", hkArray(hkbVariableInfo, hsh=2287139879)),
        Member(56, "characterPropertyInfos", hkArray(hkbVariableInfo, hsh=2287139879)),
        Member(72, "eventInfos", hkArray(hkbEventInfo, hsh=3554392229)),
        Member(88, "variableBounds", hkArray(hkbVariableBounds, hsh=3968783662)),
        Member(104, "variableInitialValues", Ptr(hkbVariableValueSet, hsh=755292339)),
        Member(112, "stringData", hkRefPtr(hkbBehaviorGraphStringData, hsh=778787014), MemberFlags.Private),
    )
    members = hkReferencedObject.members + local_members

    attributeDefaults: list[float]
    variableInfos: list[hkbVariableInfo]
    characterPropertyInfos: list[hkbVariableInfo]
    eventInfos: list[hkbEventInfo]
    variableBounds: list[hkbVariableBounds]
    variableInitialValues: hkbVariableValueSet
    stringData: hkbBehaviorGraphStringData
