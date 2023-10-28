from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hclStateDependencyGraphBranch import hclStateDependencyGraphBranch


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclStateDependencyGraph(hkReferencedObject):
    alignment = 8
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2299126301

    local_members = (
        Member(24, "branches", hkArray(hclStateDependencyGraphBranch, hsh=327981087), MemberFlags.Private),
        Member(40, "rootBranchIds", hkArray(_int, hsh=910429161), MemberFlags.Private),
        Member(56, "children", hkArray(hkArray(_int, hsh=910429161), hsh=1212383872), MemberFlags.Private),
        Member(72, "parents", hkArray(hkArray(_int, hsh=910429161), hsh=1212383872), MemberFlags.Private),
        Member(88, "multiThreadable", hkBool, MemberFlags.Private),
    )
    members = hkReferencedObject.members + local_members

    branches: list[hclStateDependencyGraphBranch]
    rootBranchIds: list[int]
    children: list[list[int]]
    parents: list[list[int]]
    multiThreadable: bool
