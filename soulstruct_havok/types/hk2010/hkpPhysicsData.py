from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkpWorldCinfo import hkpWorldCinfo
from .hkpPhysicsSystem import hkpPhysicsSystem


class hkpPhysicsData(hkReferencedObject):
    alignment = 16
    byte_size = 24
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3265552868

    local_members = (
        Member(8, "worldCinfo", Ptr(hkpWorldCinfo)),
        Member(12, "systems", hkArray(Ptr(hkpPhysicsSystem))),
    )
    members = hkReferencedObject.members + local_members

    worldCinfo: hkpWorldCinfo
    systems: list[hkpPhysicsSystem]