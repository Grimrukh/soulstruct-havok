from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbVariableBindingSetBinding import hkbVariableBindingSetBinding


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbVariableBindingSet(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2835264349
    __version = 2

    local_members = (
        Member(24, "bindings", hkArray(hkbVariableBindingSetBinding, hsh=2356897938), MemberFlags.Private),
        Member(40, "indexOfBindingToEnable", hkInt32, MemberFlags.Private),
        Member(44, "hasOutputBinding", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(45, "initializedOffsets", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkReferencedObject.members + local_members

    bindings: list[hkbVariableBindingSetBinding]
    indexOfBindingToEnable: int
    hasOutputBinding: bool
    initializedOffsets: bool
