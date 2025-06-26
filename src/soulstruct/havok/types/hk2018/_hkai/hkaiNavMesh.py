from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkaiNavMeshFace import hkaiNavMeshFace
from .hkaiNavMeshEdge import hkaiNavMeshEdge
from .hkaiAnnotatedStreamingSet import hkaiAnnotatedStreamingSet
from ..hkAabb import hkAabb
from .hkaiNavMeshClearanceCacheSeedingCacheDataSet import hkaiNavMeshClearanceCacheSeedingCacheDataSet


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiNavMesh(hkReferencedObject):
    alignment = 16
    byte_size = 208
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 4213419433
    __version = 16

    local_members = (
        Member(24, "faces", hkArray(hkaiNavMeshFace, hsh=843627853)),
        Member(40, "edges", hkArray(hkaiNavMeshEdge, hsh=1513630651)),
        Member(56, "vertices", hkArray(hkVector4, hsh=1398146255)),
        Member(72, "streamingSets", hkArray(hkaiAnnotatedStreamingSet)),
        Member(88, "faceData", hkArray(hkInt32, hsh=1517998030)),
        Member(104, "edgeData", hkArray(hkInt32, hsh=1517998030)),
        Member(120, "faceDataStriding", _int),
        Member(124, "edgeDataStriding", _int),
        Member(128, "flags", _unsigned_char, MemberFlags.Private),
        Member(144, "aabb", hkAabb),
        Member(176, "erosionRadius", hkReal),
        Member(184, "userData", hkUlong),
        Member(
            192,
            "clearanceCacheSeedingDataSet",
            hkRefPtr(hkaiNavMeshClearanceCacheSeedingCacheDataSet, hsh=4247051462),
        ),
    )
    members = hkReferencedObject.members + local_members

    faces: list[hkaiNavMeshFace]
    edges: list[hkaiNavMeshEdge]
    vertices: list[hkVector4]
    streamingSets: list[hkaiAnnotatedStreamingSet]
    faceData: list[int]
    edgeData: list[int]
    faceDataStriding: int
    edgeDataStriding: int
    flags: int
    aabb: hkAabb
    erosionRadius: float
    userData: int
    clearanceCacheSeedingDataSet: hkaiNavMeshClearanceCacheSeedingCacheDataSet
