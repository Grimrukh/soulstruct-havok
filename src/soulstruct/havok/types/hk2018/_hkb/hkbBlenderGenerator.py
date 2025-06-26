from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator
from .hkbBlenderGeneratorChild import hkbBlenderGeneratorChild


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbBlenderGenerator(hkbGenerator):
    alignment = 8
    byte_size = 240
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 53778621
    __version = 1

    local_members = (
        Member(152, "referencePoseWeightThreshold", hkReal),
        Member(156, "blendParameter", hkReal),
        Member(160, "minCyclicBlendParameter", hkReal),
        Member(164, "maxCyclicBlendParameter", hkReal),
        Member(168, "indexOfSyncMasterChild", hkInt16),
        Member(170, "flags", hkInt16),
        Member(172, "subtractLastChild", hkBool),
        Member(176, "children", hkArray(Ptr(hkbBlenderGeneratorChild, hsh=219049805), hsh=529184588)),
        Member(
            192,
            "childrenInternalStates",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(
            208,
            "sortedChildren",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Protected,
        ),
        Member(224, "endIntervalWeight", hkReal, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(228, "numActiveChildren", _int, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(232, "beginIntervalIndex", hkInt16, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(234, "endIntervalIndex", hkInt16, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(236, "initSync", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
        Member(237, "doSubtractiveBlend", hkBool, MemberFlags.NotSerializable | MemberFlags.Protected),
    )
    members = hkbGenerator.members + local_members

    referencePoseWeightThreshold: float
    blendParameter: float
    minCyclicBlendParameter: float
    maxCyclicBlendParameter: float
    indexOfSyncMasterChild: int
    flags: int
    subtractLastChild: bool
    children: list[hkbBlenderGeneratorChild]
    childrenInternalStates: list[hkReflectDetailOpaque]
    sortedChildren: list[hkReflectDetailOpaque]
    endIntervalWeight: float
    numActiveChildren: int
    beginIntervalIndex: int
    endIntervalIndex: int
    initSync: bool
    doSubtractiveBlend: bool
