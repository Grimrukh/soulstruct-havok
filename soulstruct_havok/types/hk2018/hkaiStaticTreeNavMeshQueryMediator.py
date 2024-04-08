from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkaiNavMeshQueryMediator import hkaiNavMeshQueryMediator
from .hkcdStaticAabbTree import hkcdStaticAabbTree
from .hkaiNavMesh import hkaiNavMesh


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaiStaticTreeNavMeshQueryMediator(hkaiNavMeshQueryMediator):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3425088800

    local_members = (
        Member(24, "tree", hkRefPtr(hkcdStaticAabbTree, hsh=3001532175), MemberFlags.Protected),
        Member(32, "navMesh", hkRefPtr(hkaiNavMesh, hsh=2203047159), MemberFlags.Protected),
    )
    members = hkaiNavMeshQueryMediator.members + local_members

    tree: hkcdStaticAabbTree
    navMesh: hkaiNavMesh
