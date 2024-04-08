from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkaiIndex import hkaiIndex
from .hkaiPackedKey_ import hkaiPackedKey_


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiNavMeshEdge(hk):
    alignment = 4
    byte_size = 20
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1341354419
    __version = 8
    __real_name = "hkaiNavMesh::Edge"

    local_members = (
        Member(0, "a", hkaiIndex),
        Member(4, "b", hkaiIndex),
        Member(8, "oppositeEdge", hkaiPackedKey_),
        Member(12, "oppositeFace", hkaiPackedKey_),
        Member(16, "flags", hkFlags(hkUint8)),
        Member(17, "paddingByte", hkUint8, MemberFlags.NotSerializable),
        Member(18, "userEdgeCost", hkHalf16),
    )
    members = local_members

    a: int
    b: int
    oppositeEdge: int
    oppositeFace: int
    flags: hkUint8
    paddingByte: int
    userEdgeCost: float
