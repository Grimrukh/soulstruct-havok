from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator
from .hkbTransitionEffectSelfTransitionMode import hkbTransitionEffectSelfTransitionMode
from .hkbTransitionEffectEventMode import hkbTransitionEffectEventMode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbTransitionEffect(hkbGenerator):
    alignment = 8
    byte_size = 184
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 57
    __abstract_value = 3

    local_members = (
        Member(152, "selfTransitionMode", hkEnum(hkbTransitionEffectSelfTransitionMode, hkInt8)),
        Member(153, "eventMode", hkEnum(hkbTransitionEffectEventMode, hkInt8)),
        Member(
            154,
            "defaultEventMode",
            hkEnum(hkbTransitionEffectEventMode, hkInt8),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            160,
            "patchedBindingInfo",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            168,
            "fromGenerator",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            176,
            "toGenerator",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
    )
    members = hkbGenerator.members + local_members

    selfTransitionMode: hkbTransitionEffectSelfTransitionMode
    eventMode: hkbTransitionEffectEventMode
    defaultEventMode: hkbTransitionEffectEventMode
    patchedBindingInfo: hkReflectDetailOpaque
    fromGenerator: hkReflectDetailOpaque
    toGenerator: hkReflectDetailOpaque
