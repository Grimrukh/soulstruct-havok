from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hclSimClothData import hclSimClothData
from .hclBufferDefinition import hclBufferDefinition
from .hclTransformSetDefinition import hclTransformSetDefinition
from .hclOperator import hclOperator
from .hclClothState import hclClothState
from .hclStateTransition import hclStateTransition
from .hclAction import hclAction
from .hclClothDataPlatform import hclClothDataPlatform


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclClothData(hkReferencedObject):
    alignment = 8
    byte_size = 152
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3963035682
    __version = 3

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "simClothDatas", hkArray(Ptr(hclSimClothData, hsh=2357115667), hsh=3501181651)),
        Member(48, "bufferDefinitions", hkArray(Ptr(hclBufferDefinition, hsh=78898278), hsh=2006368910)),
        Member(
            64,
            "transformSetDefinitions",
            hkArray(Ptr(hclTransformSetDefinition, hsh=360203306), hsh=3317004341),
        ),
        Member(80, "operators", hkArray(Ptr(hclOperator, hsh=2743151593), hsh=2934719668)),
        Member(96, "clothStateDatas", hkArray(Ptr(hclClothState, hsh=372743206), hsh=251459129)),
        Member(112, "stateTransitions", hkArray(Ptr(hclStateTransition))),
        Member(128, "actions", hkArray(Ptr(hclAction))),
        Member(144, "targetPlatform", hkEnum(hclClothDataPlatform, hkUint32)),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    simClothDatas: list[hclSimClothData]
    bufferDefinitions: list[hclBufferDefinition]
    transformSetDefinitions: list[hclTransformSetDefinition]
    operators: list[hclOperator]
    clothStateDatas: list[hclClothState]
    stateTransitions: list[hclStateTransition]
    actions: list[hclAction]
    targetPlatform: hclClothDataPlatform
