from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hclVirtualCollisionPointsDataBlock import hclVirtualCollisionPointsDataBlock


from .hclVirtualCollisionPointsDataBarycentricDictionaryEntry import hclVirtualCollisionPointsDataBarycentricDictionaryEntry
from .hclVirtualCollisionPointsDataBarycentricPair import hclVirtualCollisionPointsDataBarycentricPair
from .hclVirtualCollisionPointsDataEdgeFanSection import hclVirtualCollisionPointsDataEdgeFanSection
from .hclVirtualCollisionPointsDataEdgeFan import hclVirtualCollisionPointsDataEdgeFan
from .hclVirtualCollisionPointsDataTriangleFanSection import hclVirtualCollisionPointsDataTriangleFanSection
from .hclVirtualCollisionPointsDataTriangleFan import hclVirtualCollisionPointsDataTriangleFan
from .hclVirtualCollisionPointsDataEdgeFanLandscape import hclVirtualCollisionPointsDataEdgeFanLandscape
from .hclVirtualCollisionPointsDataTriangleFanLandscape import hclVirtualCollisionPointsDataTriangleFanLandscape


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclVirtualCollisionPointsData(hk):
    alignment = 8
    byte_size = 304
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "blocks", hkArray(hclVirtualCollisionPointsDataBlock)),
        Member(16, "numVCPoints", hkUint16),
        Member(24, "landscapeParticlesBlockIndex", hkArray(hkUint16, hsh=3431155310)),
        Member(40, "numLandscapeVCPoints", hkUint16),
        Member(48, "edgeBarycentricsDictionary", hkArray(hkReal, hsh=2219021489)),
        Member(64, "edgeDictionaryEntries", hkArray(hclVirtualCollisionPointsDataBarycentricDictionaryEntry)),
        Member(80, "triangleBarycentricsDictionary", hkArray(hclVirtualCollisionPointsDataBarycentricPair)),
        Member(
            96,
            "triangleDictionaryEntries",
            hkArray(hclVirtualCollisionPointsDataBarycentricDictionaryEntry),
        ),
        Member(112, "edges", hkArray(hclVirtualCollisionPointsDataEdgeFanSection)),
        Member(128, "edgeFans", hkArray(hclVirtualCollisionPointsDataEdgeFan)),
        Member(144, "triangles", hkArray(hclVirtualCollisionPointsDataTriangleFanSection)),
        Member(160, "triangleFans", hkArray(hclVirtualCollisionPointsDataTriangleFan)),
        Member(176, "edgesLandscape", hkArray(hclVirtualCollisionPointsDataEdgeFanSection)),
        Member(192, "edgeFansLandscape", hkArray(hclVirtualCollisionPointsDataEdgeFanLandscape)),
        Member(208, "trianglesLandscape", hkArray(hclVirtualCollisionPointsDataTriangleFanSection)),
        Member(224, "triangleFansLandscape", hkArray(hclVirtualCollisionPointsDataTriangleFanLandscape)),
        Member(240, "edgeFanIndices", hkArray(hkUint16, hsh=3431155310)),
        Member(256, "triangleFanIndices", hkArray(hkUint16, hsh=3431155310)),
        Member(272, "edgeFanIndicesLandscape", hkArray(hkUint16, hsh=3431155310)),
        Member(288, "triangleFanIndicesLandscape", hkArray(hkUint16, hsh=3431155310)),
    )
    members = local_members

    blocks: list[hclVirtualCollisionPointsDataBlock]
    numVCPoints: int
    landscapeParticlesBlockIndex: list[int]
    numLandscapeVCPoints: int
    edgeBarycentricsDictionary: list[float]
    edgeDictionaryEntries: list[hclVirtualCollisionPointsDataBarycentricDictionaryEntry]
    triangleBarycentricsDictionary: list[hclVirtualCollisionPointsDataBarycentricPair]
    triangleDictionaryEntries: list[hclVirtualCollisionPointsDataBarycentricDictionaryEntry]
    edges: list[hclVirtualCollisionPointsDataEdgeFanSection]
    edgeFans: list[hclVirtualCollisionPointsDataEdgeFan]
    triangles: list[hclVirtualCollisionPointsDataTriangleFanSection]
    triangleFans: list[hclVirtualCollisionPointsDataTriangleFan]
    edgesLandscape: list[hclVirtualCollisionPointsDataEdgeFanSection]
    edgeFansLandscape: list[hclVirtualCollisionPointsDataEdgeFanLandscape]
    trianglesLandscape: list[hclVirtualCollisionPointsDataTriangleFanSection]
    triangleFansLandscape: list[hclVirtualCollisionPointsDataTriangleFanLandscape]
    edgeFanIndices: list[int]
    triangleFanIndices: list[int]
    edgeFanIndicesLandscape: list[int]
    triangleFanIndicesLandscape: list[int]
