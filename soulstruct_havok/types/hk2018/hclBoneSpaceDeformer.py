from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hclBoneSpaceDeformerFourBlendEntryBlock import hclBoneSpaceDeformerFourBlendEntryBlock
from .hclBoneSpaceDeformerThreeBlendEntryBlock import hclBoneSpaceDeformerThreeBlendEntryBlock
from .hclBoneSpaceDeformerTwoBlendEntryBlock import hclBoneSpaceDeformerTwoBlendEntryBlock
from .hclBoneSpaceDeformerOneBlendEntryBlock import hclBoneSpaceDeformerOneBlendEntryBlock


class hclBoneSpaceDeformer(hk):
    alignment = 8
    byte_size = 88
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(0, "fourBlendEntries", hkArray(hclBoneSpaceDeformerFourBlendEntryBlock)),
        Member(16, "threeBlendEntries", hkArray(hclBoneSpaceDeformerThreeBlendEntryBlock)),
        Member(32, "twoBlendEntries", hkArray(hclBoneSpaceDeformerTwoBlendEntryBlock, hsh=1493222457)),
        Member(48, "oneBlendEntries", hkArray(hclBoneSpaceDeformerOneBlendEntryBlock, hsh=3238978847)),
        Member(64, "controlBytes", hkArray(hkUint8, hsh=2331026425)),
        Member(80, "startVertexIndex", hkUint16),
        Member(82, "endVertexIndex", hkUint16),
        Member(84, "partialWrite", hkBool),
    )
    members = local_members

    fourBlendEntries: list[hclBoneSpaceDeformerFourBlendEntryBlock]
    threeBlendEntries: list[hclBoneSpaceDeformerThreeBlendEntryBlock]
    twoBlendEntries: list[hclBoneSpaceDeformerTwoBlendEntryBlock]
    oneBlendEntries: list[hclBoneSpaceDeformerOneBlendEntryBlock]
    controlBytes: list[int]
    startVertexIndex: int
    endVertexIndex: int
    partialWrite: bool
