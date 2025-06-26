from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkbGenerator import hkbGenerator
from .hkbBehaviorGraphVariableMode import hkbBehaviorGraphVariableMode
from .hkbBehaviorGraphData import hkbBehaviorGraphData
from ..hkAssetRefPtr import hkAssetRefPtr


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbBehaviorGraph(hkbGenerator):
    alignment = 8
    byte_size = 440
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3088320780
    __version = 1

    local_members = (
        Member(152, "variableMode", hkEnum(hkbBehaviorGraphVariableMode, hkInt8)),
        Member(
            160,
            "uniqueIdPool",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            176,
            "idToStateMachineTemplateMap",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            184,
            "mirroredExternalIdMap",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            192,
            "pseudoRandomGenerator",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(200, "rootGenerator", hkRefPtr(hkbGenerator, hsh=1798718120), MemberFlags.Private),
        Member(208, "data", hkRefPtr(hkbBehaviorGraphData, hsh=3182137160), MemberFlags.Private),
        Member(216, "template", hkAssetRefPtr, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(
            224,
            "activeNodes",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            232,
            "globalTransitionData",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            240,
            "eventIdMap",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            248,
            "attributeIdMap",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            256,
            "variableIdMap",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            264,
            "characterPropertyIdMap",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            272,
            "animationIdMap",
            hkRefPtr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            280,
            "variableValueSet",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            288,
            "nodeTemplateToCloneMap",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            296,
            "stateListenerTemplateToCloneMap",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            304,
            "recentlyCreatedClones",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            320,
            "nodePartitionInfo",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(328, "numIntermediateOutputs", hkInt32, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(
            336,
            "intermediateOutputSizes",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(352, "jobs", hkArray(hkReflectDetailOpaque), MemberFlags.NotSerializable | MemberFlags.Private),
        Member(
            368,
            "allPartitionMemory",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            384,
            "internalToRootVariableIdMap",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            400,
            "internalToCharacterCharacterPropertyIdMap",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(
            416,
            "internalToRootAttributeIdMap",
            hkArray(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(432, "nextUniqueId", hkUint16, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(434, "isActive", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(435, "isLinked", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(436, "updateActiveNodes", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(437, "updateActiveNodesForEnable", hkBool, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(438, "checkNodeValidity", hkBool, MemberFlags.NotSerializable),
        Member(439, "stateOrTransitionChanged", hkBool, MemberFlags.NotSerializable),
    )
    members = hkbGenerator.members + local_members

    variableMode: hkbBehaviorGraphVariableMode
    uniqueIdPool: list[hkReflectDetailOpaque]
    idToStateMachineTemplateMap: hkReflectDetailOpaque
    mirroredExternalIdMap: hkReflectDetailOpaque
    pseudoRandomGenerator: hkReflectDetailOpaque
    rootGenerator: hkbGenerator
    data: hkbBehaviorGraphData
    template: hkAssetRefPtr
    activeNodes: hkReflectDetailOpaque
    globalTransitionData: hkReflectDetailOpaque
    eventIdMap: hkReflectDetailOpaque
    attributeIdMap: hkReflectDetailOpaque
    variableIdMap: hkReflectDetailOpaque
    characterPropertyIdMap: hkReflectDetailOpaque
    animationIdMap: hkReflectDetailOpaque
    variableValueSet: hkReflectDetailOpaque
    nodeTemplateToCloneMap: hkReflectDetailOpaque
    stateListenerTemplateToCloneMap: hkReflectDetailOpaque
    recentlyCreatedClones: list[hkReflectDetailOpaque]
    nodePartitionInfo: hkReflectDetailOpaque
    numIntermediateOutputs: int
    intermediateOutputSizes: list[hkReflectDetailOpaque]
    jobs: list[hkReflectDetailOpaque]
    allPartitionMemory: list[hkReflectDetailOpaque]
    internalToRootVariableIdMap: list[hkReflectDetailOpaque]
    internalToCharacterCharacterPropertyIdMap: list[hkReflectDetailOpaque]
    internalToRootAttributeIdMap: list[hkReflectDetailOpaque]
    nextUniqueId: int
    isActive: bool
    isLinked: bool
    updateActiveNodes: bool
    updateActiveNodesForEnable: bool
    checkNodeValidity: bool
    stateOrTransitionChanged: bool
