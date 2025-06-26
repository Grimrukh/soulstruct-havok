from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hknpPhysicsSystemData import hknpPhysicsSystemData
from .hknpRefWorldCinfo import hknpRefWorldCinfo


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpPhysicsSceneData(hkReferencedObject):
    alignment = 8
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3417150059
    __version = 1

    local_members = (
        Member(24, "systemDatas", hkArray(hkRefPtr(hknpPhysicsSystemData, hsh=1048860519), hsh=1607378809)),
        Member(40, "worldCinfo", Ptr(hknpRefWorldCinfo), MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    systemDatas: list[hknpPhysicsSystemData]
    worldCinfo: hknpRefWorldCinfo
