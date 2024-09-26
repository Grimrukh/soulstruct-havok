from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbNode import hkbNode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbModifier(hkbNode):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(96, "enable", hkBool),
        Member(
            97,
            "padModifier",
            hkGenericStruct(hkBool, 3),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
    )
    members = hkbNode.members + local_members

    enable: bool
    padModifier: tuple[hkBool]
