from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *



class hclStateDependencyGraphBranch(hk):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2355611125
    __real_name = "hclStateDependencyGraph::Branch"

    local_members = (
        Member(0, "branchId", _int),
        Member(8, "stateOperatorIndices", hkArray(_int, hsh=910429161)),
        Member(24, "parentBranches", hkArray(_int, hsh=910429161)),
        Member(40, "childBranches", hkArray(_int, hsh=910429161)),
    )
    members = local_members

    branchId: int
    stateOperatorIndices: list[int]
    parentBranches: list[int]
    childBranches: list[int]
