from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbScriptGenerator(hkbGenerator):
    alignment = 8
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2580381919

    local_members = (
        Member(152, "child", hkRefPtr(hkbGenerator, hsh=1798718120)),
        Member(160, "onActivateScript", hkStringPtr),
        Member(168, "onPreUpdateScript", hkStringPtr),
        Member(176, "onGenerateScript", hkStringPtr),
        Member(184, "onHandleEventScript", hkStringPtr),
        Member(192, "onDeactivateScript", hkStringPtr),
        Member(200, "refOnActivate", _int, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(204, "refOnPreUpdate", _int, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(208, "refOnGenerate", _int, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(212, "refOnHandleEvent", _int, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(216, "refOnDeactivate", _int, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(220, "timeStep", hkReal, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkbGenerator.members + local_members

    child: hkbGenerator
    onActivateScript: hkStringPtr
    onPreUpdateScript: hkStringPtr
    onGenerateScript: hkStringPtr
    onHandleEventScript: hkStringPtr
    onDeactivateScript: hkStringPtr
    refOnActivate: int
    refOnPreUpdate: int
    refOnGenerate: int
    refOnHandleEvent: int
    refOnDeactivate: int
    timeStep: float
