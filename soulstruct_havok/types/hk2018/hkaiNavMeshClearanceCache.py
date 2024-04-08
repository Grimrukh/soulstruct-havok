from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkaiNavMeshClearanceCacheMcpDataInteger import hkaiNavMeshClearanceCacheMcpDataInteger


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiNavMeshClearanceCache(hkReferencedObject):
    alignment = 8
    byte_size = 120
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 905303718
    __version = 3

    local_members = (
        Member(24, "clearanceCeiling", hkReal, MemberFlags.Protected),
        Member(28, "clearanceIntToRealMultiplier", hkReal, MemberFlags.Protected),
        Member(32, "clearanceRealToIntMultiplier", hkReal, MemberFlags.Protected),
        Member(40, "faceOffsets", hkArray(hkUint32, hsh=1109639201), MemberFlags.Protected),
        Member(56, "edgePairClearances", hkArray(hkUint8, hsh=2331026425), MemberFlags.Protected),
        Member(72, "unusedEdgePairElements", _int, MemberFlags.Protected),
        Member(
            80,
            "mcpData",
            hkArray(hkaiNavMeshClearanceCacheMcpDataInteger, hsh=3131914628),
            MemberFlags.Protected,
        ),
        Member(96, "vertexClearances", hkArray(hkUint8, hsh=2331026425), MemberFlags.Protected),
        Member(112, "uncalculatedFacesLowerBound", _int, MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    clearanceCeiling: float
    clearanceIntToRealMultiplier: float
    clearanceRealToIntMultiplier: float
    faceOffsets: list[int]
    edgePairClearances: list[int]
    unusedEdgePairElements: int
    mcpData: list[hkaiNavMeshClearanceCacheMcpDataInteger]
    vertexClearances: list[int]
    uncalculatedFacesLowerBound: int
