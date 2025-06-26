from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbVariableBindingSet import hkbVariableBindingSet


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbBindable(hkReferencedObject):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(24, "variableBindingSet", hkRefPtr(hkbVariableBindingSet, hsh=2975041933), MemberFlags.Private),
        Member(
            32,
            "cachedBindables",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(48, "areBindablesCached", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(49, "hasEnableChanged", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkReferencedObject.members + local_members

    variableBindingSet: hkbVariableBindingSet
    cachedBindables: list[hkReflectDetailOpaque]
    areBindablesCached: bool
    hasEnableChanged: bool
