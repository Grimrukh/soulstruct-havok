from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hclClothStateBufferAccess import hclClothStateBufferAccess
from .hclClothStateTransformSetAccess import hclClothStateTransformSetAccess
from .hclStateDependencyGraph import hclStateDependencyGraph


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclClothState(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3225525304
    __version = 2

    local_members = (
        Member(24, "name", hkStringPtr),
        Member(32, "operators", hkArray(hkUint32, hsh=1109639201)),
        Member(48, "usedBuffers", hkArray(hclClothStateBufferAccess, hsh=686371003)),
        Member(64, "usedTransformSets", hkArray(hclClothStateTransformSetAccess, hsh=1767586432)),
        Member(80, "usedSimCloths", hkArray(hkUint32, hsh=1109639201)),
        Member(96, "dependencyGraph", Ptr(hclStateDependencyGraph, hsh=1428167545)),
    )
    members = hkReferencedObject.members + local_members

    name: hkStringPtr
    operators: list[int]
    usedBuffers: list[hclClothStateBufferAccess]
    usedTransformSets: list[hclClothStateTransformSetAccess]
    usedSimCloths: list[int]
    dependencyGraph: hclStateDependencyGraph
