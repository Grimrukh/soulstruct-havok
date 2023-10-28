from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hclObjectSpaceDeformerEightBlendEntryBlock import hclObjectSpaceDeformerEightBlendEntryBlock
from .hclObjectSpaceDeformerSevenBlendEntryBlock import hclObjectSpaceDeformerSevenBlendEntryBlock
from .hclObjectSpaceDeformerSixBlendEntryBlock import hclObjectSpaceDeformerSixBlendEntryBlock
from .hclObjectSpaceDeformerFiveBlendEntryBlock import hclObjectSpaceDeformerFiveBlendEntryBlock
from .hclObjectSpaceDeformerFourBlendEntryBlock import hclObjectSpaceDeformerFourBlendEntryBlock
from .hclObjectSpaceDeformerThreeBlendEntryBlock import hclObjectSpaceDeformerThreeBlendEntryBlock
from .hclObjectSpaceDeformerTwoBlendEntryBlock import hclObjectSpaceDeformerTwoBlendEntryBlock
from .hclObjectSpaceDeformerOneBlendEntryBlock import hclObjectSpaceDeformerOneBlendEntryBlock


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclObjectSpaceDeformer(hk):
    alignment = 8
    byte_size = 152
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(0, "eightBlendEntries", hkArray(hclObjectSpaceDeformerEightBlendEntryBlock)),
        Member(16, "sevenBlendEntries", hkArray(hclObjectSpaceDeformerSevenBlendEntryBlock)),
        Member(32, "sixBlendEntries", hkArray(hclObjectSpaceDeformerSixBlendEntryBlock)),
        Member(48, "fiveBlendEntries", hkArray(hclObjectSpaceDeformerFiveBlendEntryBlock)),
        Member(64, "fourBlendEntries", hkArray(hclObjectSpaceDeformerFourBlendEntryBlock, hsh=3126888922)),
        Member(80, "threeBlendEntries", hkArray(hclObjectSpaceDeformerThreeBlendEntryBlock, hsh=407671142)),
        Member(96, "twoBlendEntries", hkArray(hclObjectSpaceDeformerTwoBlendEntryBlock, hsh=1065349417)),
        Member(112, "oneBlendEntries", hkArray(hclObjectSpaceDeformerOneBlendEntryBlock, hsh=2809253903)),
        Member(128, "controlBytes", hkArray(hkUint8, hsh=2331026425)),
        Member(144, "startVertexIndex", hkUint16),
        Member(146, "endVertexIndex", hkUint16),
        Member(148, "partialWrite", hkBool),
    )
    members = local_members

    eightBlendEntries: list[hclObjectSpaceDeformerEightBlendEntryBlock]
    sevenBlendEntries: list[hclObjectSpaceDeformerSevenBlendEntryBlock]
    sixBlendEntries: list[hclObjectSpaceDeformerSixBlendEntryBlock]
    fiveBlendEntries: list[hclObjectSpaceDeformerFiveBlendEntryBlock]
    fourBlendEntries: list[hclObjectSpaceDeformerFourBlendEntryBlock]
    threeBlendEntries: list[hclObjectSpaceDeformerThreeBlendEntryBlock]
    twoBlendEntries: list[hclObjectSpaceDeformerTwoBlendEntryBlock]
    oneBlendEntries: list[hclObjectSpaceDeformerOneBlendEntryBlock]
    controlBytes: list[int]
    startVertexIndex: int
    endVertexIndex: int
    partialWrite: bool
