from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator
from .hkbCustomIdSelector import hkbCustomIdSelector
from .hkbTransitionEffect import hkbTransitionEffect
from .hkbEventProperty import hkbEventProperty


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbManualSelectorGenerator(hkbGenerator):
    alignment = 8
    byte_size = 264
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3375248318
    __version = 3

    local_members = (
        Member(152, "generators", hkArray(Ptr(hkbGenerator, hsh=389751017), hsh=1309078354)),
        Member(168, "selectedGeneratorIndex", hkInt16),
        Member(176, "indexSelector", hkRefPtr(hkbCustomIdSelector, hsh=849426879)),
        Member(184, "selectedIndexCanChangeAfterActivate", hkBool),
        Member(192, "generatorChangedTransitionEffect", Ptr(hkbTransitionEffect)),
        Member(200, "sentOnClipEnd", hkbEventProperty),
        Member(216, "generatorPreDeleteIndex", hkArray(hkInt16, hsh=3571075457)),
        Member(232, "currentGeneratorIndex", hkInt16, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(234, "generatorIndexAtActivate", hkInt16, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(
            240,
            "activeTransitions",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(256, "endOfClipEventId", hkInt32),
    )
    members = hkbGenerator.members + local_members

    generators: list[hkbGenerator]
    selectedGeneratorIndex: int
    indexSelector: hkbCustomIdSelector
    selectedIndexCanChangeAfterActivate: bool
    generatorChangedTransitionEffect: hkbTransitionEffect
    sentOnClipEnd: hkbEventProperty
    generatorPreDeleteIndex: list[int]
    currentGeneratorIndex: int
    generatorIndexAtActivate: int
    activeTransitions: list[hkReflectDetailOpaque]
    endOfClipEventId: int
