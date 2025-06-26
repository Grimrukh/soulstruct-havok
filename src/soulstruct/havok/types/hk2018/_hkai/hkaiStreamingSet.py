from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkaiStreamingSetNavMeshConnection import hkaiStreamingSetNavMeshConnection
from .hkaiStreamingSetGraphConnection import hkaiStreamingSetGraphConnection
from .hkaiStreamingSetVolumeConnection import hkaiStreamingSetVolumeConnection
from ..hkAabb import hkAabb


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiStreamingSet(hkReferencedObject):
    alignment = 8
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 2

    local_members = (
        Member(24, "aSectionUid", hkUint32),
        Member(28, "bSectionUid", hkUint32),
        Member(32, "meshConnections", hkArray(hkaiStreamingSetNavMeshConnection)),
        Member(48, "graphConnections", hkArray(hkaiStreamingSetGraphConnection)),
        Member(64, "volumeConnections", hkArray(hkaiStreamingSetVolumeConnection)),
        Member(80, "aConnectionAabbs", hkArray(hkAabb)),
        Member(96, "bConnectionAabbs", hkArray(hkAabb)),
    )
    members = hkReferencedObject.members + local_members

    aSectionUid: int
    bSectionUid: int
    meshConnections: list[hkaiStreamingSetNavMeshConnection]
    graphConnections: list[hkaiStreamingSetGraphConnection]
    volumeConnections: list[hkaiStreamingSetVolumeConnection]
    aConnectionAabbs: list[hkAabb]
    bConnectionAabbs: list[hkAabb]
