from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


from .hkaiIndex import hkaiIndex


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiNavMeshFace(hk):
    alignment = 4
    byte_size = 16
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2544818591
    __version = 6
    __real_name = "hkaiNavMesh::Face"

    local_members = (
        Member(0, "startEdgeIndex", hkaiIndex),
        Member(4, "startUserEdgeIndex", hkaiIndex),
        Member(8, "numEdges", hkInt16),
        Member(10, "numUserEdges", hkInt16),
        Member(12, "clusterIndex", hkInt16),
        Member(14, "padding", hkUint16),
    )
    members = local_members

    startEdgeIndex: int
    startUserEdgeIndex: int
    numEdges: int
    numUserEdges: int
    clusterIndex: int
    padding: int
