from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator
from .hkbModifier import hkbModifier


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbModifierGenerator(hkbGenerator):
    alignment = 8
    byte_size = 168
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 905081360

    local_members = (
        Member(152, "modifier", hkRefPtr(hkbModifier, hsh=2519142067)),
        Member(160, "generator", hkRefPtr(hkbGenerator, hsh=1798718120)),
    )
    members = hkbGenerator.members + local_members

    modifier: hkbModifier
    generator: hkbGenerator
