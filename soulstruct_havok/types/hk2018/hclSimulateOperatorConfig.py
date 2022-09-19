from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *






class hclSimulateOperatorConfig(hk):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3570302244
    __real_name = "hclSimulateOperator::Config"

    local_members = (
        Member(0, "name", hkStringPtr),
        Member(8, "constraintExecution", hkArray(hkInt32, hsh=1517998030)),
        Member(24, "instanceCollidablesUsed", hkArray(hkBool, hsh=3977017243)),
        Member(40, "subSteps", hkUint8),
        Member(41, "numberOfSolveIterations", hkUint8),
        Member(42, "useAllInstanceCollidables", hkBool),
        Member(43, "adaptConstraintStiffness", hkBool),
    )
    members = local_members

    name: hkStringPtr
    constraintExecution: list[int]
    instanceCollidablesUsed: list[bool]
    subSteps: int
    numberOfSolveIterations: int
    useAllInstanceCollidables: bool
    adaptConstraintStiffness: bool
