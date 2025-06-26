from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkpWorldCinfo import hkpWorldCinfo
from .hkpPhysicsSystem import hkpPhysicsSystem


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpPhysicsData(hkReferencedObject):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3659538096

    local_members = (
        Member(16, "worldCinfo", Ptr(hkpWorldCinfo), MemberFlags.Protected),
        Member(
            24,
            "systems",
            hkArray(Ptr(hkpPhysicsSystem, hsh=339365373), hsh=4005313520),
            MemberFlags.Protected,
        ),
    )
    members = hkReferencedObject.members + local_members

    worldCinfo: hkpWorldCinfo | None
    systems: list[hkpPhysicsSystem]
