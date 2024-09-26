from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkb.hkbBlendingTransitionEffect import hkbBlendingTransitionEffect


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class CustomTransitionEffect(hkbBlendingTransitionEffect):
    alignment = 16
    byte_size = 368
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 1297775428

    local_members = (
        Member(352, "durationBackup", hkReal, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(356, "calcDuration", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkbBlendingTransitionEffect.members + local_members

    durationBackup: float
    calcDuration: bool
