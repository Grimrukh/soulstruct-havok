from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbVariableValue import hkbVariableValue


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbVariableValueSet(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1750627109
    __version = 1

    local_members = (
        Member(24, "wordVariableValues", hkArray(hkbVariableValue, hsh=537349143), MemberFlags.Private),
        Member(40, "quadVariableValues", hkArray(hkVector4, hsh=1398146255), MemberFlags.Private),
        Member(
            56,
            "variantVariableValues",
            hkArray(hkRefVariant(hkReferencedObject, hsh=340571500)),
            MemberFlags.Private,
        ),
    )
    members = hkReferencedObject.members + local_members

    wordVariableValues: list[hkbVariableValue]
    quadVariableValues: list[hkVector4]
    variantVariableValues: list[hkReferencedObject]
